"""TuskApp dashboard endpoints. Login, logout, password reset, accounts and notifications come from MSFLib routers."""

import secrets
from datetime import date, datetime, time, timedelta
from pathlib import Path
from types import SimpleNamespace
from typing import Annotated, Any

from fastapi import APIRouter, HTTPException, Query, Response, UploadFile, status
from msflib.core.security import create_access_token
from msflib.utils.file import get_upload_url_file_path
from msflib.utils.uploads import StorageMethod, save_file, validate_upload
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import func
from sqlmodel import col, select

from tusk_mcp import views
from tusk_mcp.actions import account_action, profile_action
from tusk_mcp.api.deps import CurrentAccount, CurrentBusiness, SessionDep
from tusk_mcp.core.config import settings
from tusk_mcp.models import (
    AccountCreate,
    AccountRead,
    Booking,
    Customer,
    Enquiry,
    McpCallLog,
    McpToken,
    Payment,
    utcnow,
)
from tusk_mcp.services import business as biz
from tusk_mcp.services import catalogue, chats
from tusk_mcp.services.business import LAGOS, Business, naira
from tusk_mcp.services.tokens import issue_mcp_token, list_mcp_tokens

router = APIRouter()

ABOUT_MAX = 1000


# Signup (login and logout are MSFLib's /login and /logout)


class SignupIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=32)
    password: str = Field(min_length=8, max_length=128)
    business_name: str = Field(min_length=2, max_length=120)
    category: str = ""
    area: str = ""
    about: str = Field("", max_length=ABOUT_MAX)


@router.post("/auth/signup", status_code=status.HTTP_201_CREATED, tags=["auth"])
def signup(body: SignupIn, session: SessionDep) -> dict[str, Any]:
    email = body.email.lower()
    if account_action.get_by_email(session, email=email):
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists.")
    phone = biz.account_phone(body.phone)
    if account_action.get_by_all(session, phone=phone):
        phone = None
    account = account_action.create(
        session,
        data=AccountCreate(
            email=email,
            phone=phone,
            password=body.password,
            data={"kind": "owner"},
            profile=biz.profile_for(body.name),
        ),
        commit=False,
    )
    biz.create_business(
        session, account, body.business_name, category=body.category, area=body.area, about=body.about
    )
    session.commit()
    expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(account.email, settings.SECRET_KEY, expires),
        "token_type": "bearer",
        "expires": datetime.now(LAGOS) + expires,
        "account": AccountRead.model_validate(account),
    }


# Account and business


def _payments_mode() -> str:
    key = settings.PAYSTACK_SECRET_KEY
    if not key:
        return "test"
    return "paystack-live" if key.startswith("sk_live_") else "paystack-test"


def _business_out(business: Business) -> dict[str, Any]:
    return {
        "id": business.id,
        "slug": business.slug,
        "name": business.name,
        "category": business.category,
        "area": business.area,
        "address": business.address,
        "about": business.about,
        "whatsapp": business.whatsapp,
        "cover_photo": business.cover_photo,
        "deposit_naira": business.deposit_kobo // 100,
        "policies": business.policies,
        "hours": [
            {"weekday": d, "open": o.strftime("%H:%M"), "close": c.strftime("%H:%M")}
            for d, o, c in business.hours
        ],
        "home_service": business.home_service,
        "home_service_fee_naira": business.home_service_fee_kobo // 100,
        "located": business.location is not None,
        "profile_url": business.profile_url,
        "customer_mcp_url": f"{settings.PUBLIC_BASE_URL}/mcp/customer/?b={business.slug}",
        "owner_mcp_url": f"{settings.PUBLIC_BASE_URL}/mcp/owner/",
        "payments": _payments_mode(),
    }


@router.get("/me", tags=["account"])
def me(account: CurrentAccount, business: CurrentBusiness) -> dict[str, Any]:
    return {"user": views.user_detail(account), "business": _business_out(business)}


class ProfileIn(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=120)
    phone: str | None = Field(None, min_length=7, max_length=32)


@router.patch("/me", tags=["account"])
def update_me(body: ProfileIn, session: SessionDep, account: CurrentAccount, business: CurrentBusiness) -> dict[str, Any]:
    if body.name is not None and account.profile is not None:
        names = biz.profile_for(body.name)
        profile_action.update(
            session, model=account.profile, update=names.model_dump(include={"first_name", "last_name"}), commit=False
        )
    if body.phone is not None:
        phone = biz.account_phone(body.phone)
        account_action.ensure_unique_fields(
            session,
            data=SimpleNamespace(phone=phone),
            fields=["phone"],
            exclude_account_id=account.id,
            error_detail="Another account already uses this phone number.",
        )
        account_action.update(session, model=account, update={"phone": phone}, commit=False)
    session.commit()
    session.refresh(account)
    return me(account, business)


class HoursIn(BaseModel):
    weekday: int = Field(ge=0, le=6)
    open: time
    close: time


class BusinessIn(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=120)
    category: str | None = None
    area: str | None = None
    address: str | None = None
    about: str | None = Field(None, max_length=ABOUT_MAX)
    whatsapp: str | None = Field(None, max_length=32)
    deposit_naira: int | None = Field(None, ge=0)
    home_service: bool | None = None
    home_service_fee_naira: int | None = Field(None, ge=0)
    policies: list[str] | None = None
    hours: list[HoursIn] | None = None

    @field_validator("whatsapp")
    @classmethod
    def whatsapp_number(cls, value: str | None) -> str | None:
        if value and biz.whatsapp_link(value) is None:
            raise ValueError("Enter a full WhatsApp number, e.g. 0803 123 4567.")
        return value.strip() if value is not None else None


@router.patch("/business", tags=["business"])
def update_business(body: BusinessIn, session: SessionDep, business: CurrentBusiness) -> dict[str, Any]:
    biz.update_profile(
        session,
        business,
        **body.model_dump(include={"name", "category", "area", "address", "about", "whatsapp"}),
    )
    config: dict[str, Any] = {}
    if body.deposit_naira is not None:
        config["deposit_kobo"] = body.deposit_naira * 100
    if body.home_service is not None:
        config["home_service"] = body.home_service
    if body.home_service_fee_naira is not None:
        config["home_service_fee_kobo"] = body.home_service_fee_naira * 100
    if body.policies is not None:
        config["policies"] = [p.strip() for p in body.policies if p.strip()]
    if body.hours is not None:
        if any(h.close <= h.open for h in body.hours):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Closing time must be after opening time.")
        config["hours"] = biz.hours_to_config([(h.weekday, h.open, h.close) for h in body.hours])
    session.commit()
    if config:
        biz.save_booking_config(session, business.id, **config)
    return _business_out(biz.load_business(session, business.workspace))


# Public business profiles (no login): SITE_URL/<slug>


@router.get("/public/businesses", tags=["public"])
def public_businesses(session: SessionDep) -> list[dict[str, Any]]:
    return [views.business_summary(b) for b in biz.open_businesses(session)]


@router.get("/public/businesses/{slug}", tags=["public"])
def public_business(slug: str, session: SessionDep) -> dict[str, Any]:
    business = biz.business_by_slug(session, slug)
    return {
        **views.business_detail(business),
        "services": [views.service_card(s) for s in biz.list_services(session, business)],
        "customer_mcp_url": f"{settings.PUBLIC_BASE_URL}/mcp/customer/?b={business.slug}",
    }


# Services


class ServiceIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str = ""
    price_naira: int = Field(gt=0)
    duration_min: int = Field(gt=0)
    is_published: bool = True


class ServicePatch(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=120)
    description: str | None = None
    price_naira: int | None = Field(None, gt=0)
    duration_min: int | None = Field(None, gt=0)
    is_published: bool | None = None


@router.get("/services", tags=["services"])
def services(session: SessionDep, business: CurrentBusiness) -> list[dict[str, Any]]:
    return [views.service_card(s) for s in biz.list_services(session, business, published_only=False)]


@router.post("/services", status_code=status.HTTP_201_CREATED, tags=["services"])
def create_service(body: ServiceIn, session: SessionDep, business: CurrentBusiness) -> dict[str, Any]:
    service = biz.add_service(
        session,
        business,
        name=body.name,
        price_kobo=body.price_naira * 100,
        duration_min=body.duration_min,
        description=body.description,
        is_published=body.is_published,
    )
    session.commit()
    return views.service_card(service)


@router.patch("/services/{service_id}", tags=["services"])
def edit_service(service_id: int, body: ServicePatch, session: SessionDep, business: CurrentBusiness) -> dict[str, Any]:
    changes = body.model_dump(exclude_none=True, exclude={"price_naira"})
    if body.price_naira is not None:
        changes["price_kobo"] = body.price_naira * 100
    service = biz.update_service(session, business, service_id, **changes)
    session.commit()
    return views.service_card(service)


@router.delete("/services/{service_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["services"])
def delete_service(service_id: int, session: SessionDep, business: CurrentBusiness) -> Response:
    service = biz.get_service(session, business, service_id)
    if session.exec(select(Booking.id).where(Booking.service_id == service.id).limit(1)).first():
        service.is_published = False
        session.add(service)
    else:
        session.delete(service)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


CATALOGUE_MAX_BYTES = 1024 * 1024
CATALOGUE_TYPES = ["text/csv", "application/csv", "application/vnd.ms-excel", "text/plain", "application/octet-stream"]


@router.post("/services/import", tags=["services"])
def import_services(file: UploadFile, session: SessionDep, business: CurrentBusiness) -> dict[str, Any]:
    """Create or update services from a CSV price list (name, price, duration, description, published)."""
    validate_upload(file, max_bytes=CATALOGUE_MAX_BYTES, allowed_content_types=CATALOGUE_TYPES)
    if not (file.filename or "").lower().endswith((".csv", ".txt")):
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Save the sheet as CSV first (File → Download → CSV)."
        )
    try:
        result = catalogue.import_catalogue(session, business, file.file.read())
    except catalogue.CatalogueError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from exc
    session.commit()
    return result.view()


@router.get("/services/import/template", tags=["services"])
def services_template() -> Response:
    return Response(
        catalogue.TEMPLATE,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="tuskapp-price-list.csv"'},
    )


PHOTO_MAX_BYTES = 5 * 1024 * 1024
PHOTO_TYPES = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


@router.post("/services/{service_id}/photos", status_code=status.HTTP_201_CREATED, tags=["services"])
def upload_service_photo(
    service_id: int, photo: UploadFile, session: SessionDep, business: CurrentBusiness
) -> dict[str, Any]:
    service = biz.get_service(session, business, service_id)
    if len(service.photo_urls) >= biz.MAX_SERVICE_PHOTOS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Up to {biz.MAX_SERVICE_PHOTOS} photos per service.")
    validate_upload(photo, max_bytes=PHOTO_MAX_BYTES, allowed_content_types=list(PHOTO_TYPES))
    method = StorageMethod(settings.STORAGE_METHOD)
    folder = f"workspace/{business.id}/services"
    if method in (StorageMethod.s3, StorageMethod.gcs, StorageMethod.azure):
        # These MSFLib backends take the bucket/container as `parent_folder` and the path as `storage_bucket`.
        if not settings.STORAGE_BUCKET:
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Photo storage isn't set up (STORAGE_BUCKET).")
        parent_folder, storage_bucket = settings.STORAGE_BUCKET, folder
    else:
        parent_folder, storage_bucket = f"workspace/{business.id}", "services"
    url = save_file(
        photo,
        parent_folder=parent_folder,
        storage_bucket=storage_bucket,
        filename=f"{secrets.token_hex(16)}.{PHOTO_TYPES[photo.content_type or '']}",
        settings=settings,
        storage_method=method,
    )
    service = biz.set_service_photos(session, business, service_id, [*service.photo_urls, url])
    session.commit()
    return views.service_card(service)


@router.delete("/services/{service_id}/photos", tags=["services"])
def remove_service_photo(
    service_id: int, url: Annotated[str, Query()], session: SessionDep, business: CurrentBusiness
) -> dict[str, Any]:
    service = biz.get_service(session, business, service_id)
    stored = next((u for u in service.photo_urls if biz.media_url(u) == url or u == url), None)
    if stored is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "That photo isn't on this service.")
    if settings.STORAGE_METHOD == StorageMethod.file and stored.startswith(settings.STORAGE_BASE_URL):
        Path(get_upload_url_file_path(stored, settings)).unlink(missing_ok=True)
    service = biz.set_service_photos(session, business, service_id, [u for u in service.photo_urls if u != stored])
    session.commit()
    return views.service_card(service)


# Bookings


def _booking_out(session: SessionDep, booking: Booking) -> dict[str, Any]:
    payment = session.get(Payment, booking.payment_id) if booking.payment_id else None
    return views.booking_detail(booking, payment)


@router.get("/bookings", tags=["bookings"])
def bookings(
    session: SessionDep,
    business: CurrentBusiness,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    day: date | None = None,
) -> list[dict[str, Any]]:
    found = biz.list_bookings(session, business, day, status_filter)
    session.commit()
    return [_booking_out(session, b) for b in found]


@router.post("/bookings/{ref}/confirm", tags=["bookings"])
def confirm_booking(ref: str, session: SessionDep, business: CurrentBusiness) -> dict[str, Any]:
    """Marks a deposit as paid outside the payment link (cash, bank transfer)."""
    booking = biz.confirm_booking(session, biz.business_booking(session, business, ref))
    session.commit()
    return _booking_out(session, booking)


@router.post("/bookings/{ref}/cancel", tags=["bookings"])
def cancel_booking(ref: str, session: SessionDep, business: CurrentBusiness) -> dict[str, Any]:
    booking = biz.cancel_booking(session, business, ref)
    session.commit()
    return _booking_out(session, booking)


# Customers


class CustomerIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    phone: str = Field(min_length=7, max_length=32)
    email: EmailStr | None = None


class CustomerPatch(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=120)
    phone: str | None = Field(None, min_length=7, max_length=32)
    email: EmailStr | None = None


@router.get("/customers", tags=["customers"])
def customers(session: SessionDep, business: CurrentBusiness, q: str | None = None) -> list[dict[str, Any]]:
    return [views.customer_detail(c) for c in biz.list_customers(session, business, q)]


@router.post("/customers", status_code=status.HTTP_201_CREATED, tags=["customers"])
def add_customer(body: CustomerIn, session: SessionDep, business: CurrentBusiness) -> dict[str, Any]:
    customer = biz.upsert_customer(session, business, body.name, body.phone, body.email, source="dashboard")
    session.commit()
    return views.customer_detail(customer)


@router.get("/customers/{customer_id}", tags=["customers"])
def customer(customer_id: int, session: SessionDep, business: CurrentBusiness) -> dict[str, Any]:
    found = biz.get_customer(session, business, customer_id)
    enquiries = session.exec(
        select(Enquiry).where(Enquiry.customer_id == found.id).order_by(col(Enquiry.asked_at).desc())
    )
    return {
        **views.customer_detail(found),
        "booking_history": [
            _booking_out(session, b) for b in sorted(found.bookings, key=lambda b: b.start, reverse=True)
        ],
        "questions": [views.enquiry_detail(e) for e in enquiries],
        "chat": chats.transcript(session, business, found),
    }


@router.patch("/customers/{customer_id}", tags=["customers"])
def edit_customer(
    customer_id: int, body: CustomerPatch, session: SessionDep, business: CurrentBusiness
) -> dict[str, Any]:
    found = biz.get_customer(session, business, customer_id)
    if body.phone is not None:
        key = biz.phone_key(body.phone)
        clash = session.exec(
            select(Customer.id).where(
                Customer.workspace_id == business.id, Customer.phone_key == key, Customer.id != found.id
            )
        ).first()
        if clash:
            raise HTTPException(status.HTTP_409_CONFLICT, "Another customer already has this phone number.")
        found.phone, found.phone_key = body.phone, key
    if body.name is not None:
        found.name = body.name
    if "email" in body.model_fields_set:
        found.email = body.email
    session.add(found)
    session.commit()
    session.refresh(found)
    return views.customer_detail(found)


# Questions customers asked that the business's data didn't answer


class AnswerIn(BaseModel):
    answer: str = Field(min_length=1)
    add_to_policies: bool = True


@router.get("/enquiries", tags=["enquiries"])
def enquiries(
    session: SessionDep,
    business: CurrentBusiness,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
) -> list[dict[str, Any]]:
    stmt = select(Enquiry).where(Enquiry.workspace_id == business.id).order_by(col(Enquiry.asked_at).desc())
    if status_filter:
        stmt = stmt.where(Enquiry.status == status_filter)
    return [views.enquiry_detail(e) for e in session.exec(stmt)]


@router.post("/enquiries/{enquiry_id}/answer", tags=["enquiries"])
def answer_enquiry(
    enquiry_id: int, body: AnswerIn, session: SessionDep, account: CurrentAccount, business: CurrentBusiness
) -> dict[str, Any]:
    enquiry = session.get(Enquiry, enquiry_id)
    if enquiry is None or enquiry.workspace_id != business.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not found.")
    enquiry.answer = body.answer.strip()
    enquiry.status = "answered"
    session.add(enquiry)
    session.commit()
    if body.add_to_policies:
        biz.save_booking_config(session, business.id, policies=[*business.policies, enquiry.answer])
    session.refresh(enquiry)
    result = views.enquiry_detail(enquiry)
    if enquiry.customer_id is not None:
        workspace_id, customer_id = business.id, enquiry.customer_id
        reply = f"{biz.full_name(account).split()[0]} from {business.name} replied: {enquiry.answer}"
        session.close()
        chats.record_chat(workspace_id, customer_id, [("assistant", reply)])
    return result


# Overview


def _activity(session: SessionDep, business: Business, limit: int = 25) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for b in session.exec(
        select(Booking)
        .where(Booking.workspace_id == business.id)
        .order_by(col(Booking.booked_at).desc())
        .limit(limit)
    ):
        start = b.start.astimezone(LAGOS)
        items.append(
            {
                "id": f"booking-{b.ref}",
                "kind": "booking",
                "title": f"{b.customer.name} booked {b.service_name}",
                "subtitle": f"{b.ref} · {start:%a %d %b}, {biz.time_label(start)}",
                "amount": naira(b.total_kobo),
                "status": b.status,
                "at": b.booked_at.isoformat(),
            }
        )
    for e in session.exec(
        select(Enquiry)
        .where(Enquiry.workspace_id == business.id)
        .order_by(col(Enquiry.asked_at).desc())
        .limit(limit)
    ):
        items.append(
            {
                "id": f"enquiry-{e.id}",
                "kind": "question",
                "title": f"{e.customer.name if e.customer else 'A customer'} asked a question",
                "subtitle": e.question,
                "amount": None,
                "status": e.status,
                "at": e.asked_at.isoformat(),
            }
        )
    for log in session.exec(
        select(McpCallLog)
        .where(McpCallLog.workspace_id == business.id, McpCallLog.server == "customer")
        .order_by(col(McpCallLog.called_at).desc())
        .limit(limit)
    ):
        items.append(
            {
                "id": f"call-{log.id}",
                "kind": "chat",
                "title": log.tool.replace("_", " ").capitalize(),
                "subtitle": "From ChatGPT / Claude",
                "amount": None,
                "status": log.status,
                "at": log.called_at.isoformat(),
            }
        )
    return sorted(items, key=lambda item: item["at"], reverse=True)[:limit]


@router.get("/overview", tags=["overview"])
def overview(session: SessionDep, business: CurrentBusiness) -> dict[str, Any]:
    all_bookings = biz.list_bookings(session, business)
    session.commit()
    today = datetime.now(LAGOS).date()
    now = utcnow()
    week_ago = now - timedelta(days=7)
    chat_calls = session.exec(
        select(func.count(McpCallLog.id)).where(
            McpCallLog.workspace_id == business.id,
            McpCallLog.server == "customer",
            McpCallLog.called_at >= week_ago,
        )
    ).one()
    open_questions = session.exec(
        select(func.count(Enquiry.id)).where(Enquiry.workspace_id == business.id, Enquiry.status == "open")
    ).one()
    customer_count = session.exec(
        select(func.count(Customer.id)).where(Customer.workspace_id == business.id)
    ).one()
    confirmed = [b for b in all_bookings if b.status == "confirmed"]
    upcoming = [b for b in all_bookings if b.status in biz.ACTIVE and b.start >= now]
    return {
        "stats": {
            "bookings_today": sum(
                1 for b in all_bookings if b.status in biz.ACTIVE and b.start.astimezone(LAGOS).date() == today
            ),
            "upcoming_bookings": len(upcoming),
            "awaiting_deposit": sum(1 for b in all_bookings if b.status == "held"),
            "deposits_collected": naira(sum(b.deposit_kobo for b in confirmed)),
            "booked_value": naira(sum(b.total_kobo for b in confirmed)),
            "customers": customer_count,
            "chat_requests_7d": chat_calls,
            "open_questions": open_questions,
        },
        "upcoming": [_booking_out(session, b) for b in upcoming[:6]],
        "insights": biz.insights(session, business),
        "activity": _activity(session, business),
    }


# Owner MCP tokens


class TokenIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)


def _token_out(token: McpToken) -> dict[str, Any]:
    return {
        "id": token.id,
        "name": token.name,
        "prefix": token.prefix,
        "created_at": views.iso(token.issued_at),
        "last_used_at": views.iso(token.last_used_at),
    }


@router.get("/mcp-tokens", tags=["mcp"])
def mcp_tokens(session: SessionDep, business: CurrentBusiness) -> list[dict[str, Any]]:
    return [_token_out(t) for t in list_mcp_tokens(session, business)]


@router.post("/mcp-tokens", status_code=status.HTTP_201_CREATED, tags=["mcp"])
def create_mcp_token(
    body: TokenIn, session: SessionDep, account: CurrentAccount, business: CurrentBusiness
) -> dict[str, Any]:
    row, token = issue_mcp_token(session, business, account, body.name)
    session.commit()
    return {**_token_out(row), "token": token}


@router.delete("/mcp-tokens/{token_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["mcp"])
def delete_mcp_token(token_id: int, session: SessionDep, business: CurrentBusiness) -> Response:
    row = session.get(McpToken, token_id)
    if row is None or row.workspace_id != business.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Token not found.")
    session.delete(row)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
