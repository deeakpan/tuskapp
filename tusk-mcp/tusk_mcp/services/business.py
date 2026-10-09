"""Businesses, services, customers and bookings, shared by the MCP tools and the dashboard API.

A business is an MSFLib workspace: profile fields live on `Workspace.data`, booking settings
(hours, deposit, policies) in `workspace_config`, and every customer has an MSFLib account.
"""

import re
import secrets
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Any
from urllib.parse import quote, quote_plus

from msflib.utils.utils import slugify
from msflib.workspace_config.models import ConfigScopeType
from sqlalchemy import func, or_, update
from sqlmodel import Session, col, select

from tusk_mcp.actions import (
    account_action,
    blocked_slot_action,
    booking_action,
    call_log_action,
    config_service,
    customer_action,
    enquiry_action,
    service_action,
    tenant_action,
    user_action,
    workspace_action,
)
from tusk_mcp.core.config import settings
from tusk_mcp.services import geo
from tusk_mcp.models import (
    Account,
    AccountCreate,
    BlockedSlot,
    BlockedSlotCreate,
    Booking,
    BookingCreate,
    Customer,
    CustomerCreate,
    Enquiry,
    EnquiryCreate,
    McpCallLog,
    McpCallLogCreate,
    ProfileCreate,
    Service,
    ServiceCreate,
    User,
    UserType,
    Workspace,
    WorkspaceCreate,
    WorkspaceStatus,
    utcnow,
)

LAGOS = timezone(timedelta(hours=1), "WAT")
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
SLOT_STEP = timedelta(minutes=60)
ACTIVE = ("held", "confirmed")
BOOKING_CONFIG = "TUSK_BOOKING"
CUSTOMER_EMAIL_DOMAIN = "customers.tuskapp.app"
FIRST_REF = 412
# Top-level paths the website uses itself, so no business profile can take them.
RESERVED_SLUGS = {
    "about", "admin", "api", "apple-icon", "auth", "b", "bookings", "customers", "help", "icon", "login",
    "mcp", "opengraph-image", "pay", "privacy", "questions", "robots", "services", "settings", "signup",
    "sitemap", "support", "terms", "twitter-image", "welcome",
}

_STOPWORDS = {
    "a", "an", "and", "any", "are", "at", "be", "can", "do", "does", "for", "get", "have",
    "how", "i", "in", "is", "it", "me", "much", "my", "of", "on", "or", "she", "that", "the",
    "there", "they", "to", "what", "when", "where", "which", "who", "with", "you", "your",
}


class NotFound(Exception):
    pass


class BookingError(Exception):
    pass


def naira(kobo: int) -> str:
    return f"₦{kobo / 100:,.0f}"


def duration_label(minutes: int) -> str:
    if minutes < 60:
        return f"{minutes} mins"
    hours = minutes / 60
    return f"{hours:g} hr" if hours == 1 else f"{hours:g} hrs"


def time_label(value: datetime | time) -> str:
    return value.strftime("%I:%M%p").lstrip("0").lower()


def when_label(start: datetime) -> str:
    local = start.astimezone(LAGOS)
    return f"{local.strftime('%a %d %b')} at {time_label(local)}"


PLACEHOLDER_PHOTO = "https://placehold.co/"


def photo_url(text: str) -> str:
    return f"{PLACEHOLDER_PHOTO}600x400/1b1d1c/e8efe9?text={quote_plus(text)}"


def media_url(url: str) -> str:
    """Uploads are stored relative to STORAGE_BASE_URL (MSFLib's convention); chat apps need absolute links."""
    base = settings.STORAGE_BASE_URL
    if base.startswith("/") and url.startswith(base):
        return f"{settings.PUBLIC_BASE_URL.rstrip('/')}{url}"
    return url


def phone_key(phone: str) -> str:
    return re.sub(r"\D", "", phone)[-10:]


def account_phone(phone: str) -> str:
    """One stored form per number, so 0803… and +234 803… find the same MSFLib account."""
    key = phone_key(phone)
    return f"+234{key}" if len(key) == 10 else key


def whatsapp_link(phone: str, text: str = "") -> str | None:
    """A wa.me click-to-chat link that opens WhatsApp with `text` already typed."""
    number = account_phone(phone).lstrip("+")
    if len(number) < 10:
        return None
    return f"https://wa.me/{number}" + (f"?text={quote(text)}" if text else "")


def keywords(text: str) -> set[str]:
    words = set()
    for word in re.findall(r"[a-z0-9]+", text.lower()):
        if word in _STOPWORDS or len(word) < 2:
            continue
        words.add(_singular(word))
    return words


def _singular(word: str) -> str:
    if len(word) > 4 and word.endswith(("ches", "shes", "sses", "xes")):
        return word[:-2]
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def full_name(account: Account) -> str:
    profile = account.profile
    if profile is not None:
        name = " ".join(p for p in (profile.first_name, profile.last_name) if p)
        if name:
            return name
    return account.username or account.email.split("@")[0]


def profile_for(name: str) -> ProfileCreate:
    first, _, last = name.strip().partition(" ")
    return ProfileCreate(first_name=first or name, last_name=last or None)


# Businesses


@dataclass
class Business:
    workspace: Workspace
    owner: Account
    deposit_kobo: int
    policies: list[str]
    hours: list[tuple[int, time, time]]
    home_service: bool = False
    home_service_fee_kobo: int = 0

    @property
    def id(self) -> int:
        return self.workspace.id

    @property
    def slug(self) -> str:
        return self.workspace.slug

    @property
    def name(self) -> str:
        return self.workspace.name

    def _data(self, key: str, default: Any = "") -> Any:
        return (self.workspace.data or {}).get(key, default)

    @property
    def category(self) -> str:
        return self._data("category")

    @property
    def area(self) -> str:
        return self._data("area")

    @property
    def address(self) -> str:
        return self._data("address")

    @property
    def about(self) -> str:
        """The owner's own description: specialities, who they serve, what makes them different."""
        return self.workspace.description or ""

    @property
    def whatsapp(self) -> str:
        return self._data("whatsapp")

    @property
    def location(self) -> geo.Point | None:
        lat, lng = self._data("lat", None), self._data("lng", None)
        return (float(lat), float(lng)) if lat is not None and lng is not None else None

    @property
    def profile_url(self) -> str:
        return f"{settings.SITE_URL.rstrip('/')}/{self.slug}"

    def whatsapp_url(self, text: str = "") -> str | None:
        return whatsapp_link(self.whatsapp, text) if self.whatsapp else None

    @property
    def ref_prefix(self) -> str:
        return self._data("ref_prefix", "TSK")

    @property
    def cover_photo(self) -> str:
        return media_url(self.workspace.logo_url) if self.workspace.logo_url else photo_url(self.name)

    @property
    def owner_name(self) -> str:
        return full_name(self.owner)


def profile_slug(name: str, area: str = "") -> str:
    """The business's profile path (SITE_URL/<slug>), kept clear of the website's own pages."""
    slug = slugify(name)
    if slug in RESERVED_SLUGS:
        slug = f"{slug}-{slugify(area.split(',')[0]) or 'ng'}"
    return slug


def _ref_prefix(name: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", name)
    prefix = "".join(w[0] for w in words) if len(words) > 1 else (words[0] if words else "TSK")
    return prefix[:3].upper().ljust(3, "X")


def hours_to_config(hours: list[tuple[int, time, time]]) -> list[dict[str, Any]]:
    return [{"weekday": d, "open": o.strftime("%H:%M"), "close": c.strftime("%H:%M")} for d, o, c in hours]


def hours_from_config(rows: list[dict[str, Any]]) -> list[tuple[int, time, time]]:
    return sorted(
        (int(r["weekday"]), time.fromisoformat(r["open"]), time.fromisoformat(r["close"])) for r in rows
    )


def booking_config(session: Session, workspace_id: int) -> dict[str, Any]:
    return config_service.get_namespace_values(
        session, ConfigScopeType.workspace, BOOKING_CONFIG, workspace_id=workspace_id
    )


def save_booking_config(session: Session, workspace_id: int, **changes: Any) -> None:
    values = booking_config(session, workspace_id)
    values.update(changes)
    config_service.put_namespace_values(
        session, ConfigScopeType.workspace, BOOKING_CONFIG, values, workspace_id=workspace_id
    )


def load_business(session: Session, workspace: Workspace) -> Business:
    config = booking_config(session, workspace.id)
    return Business(
        workspace=workspace,
        owner=account_action.get(session, workspace.owner_id),
        deposit_kobo=int(config.get("deposit_kobo", 0)),
        policies=list(config.get("policies", [])),
        hours=hours_from_config(config.get("hours", [])),
        home_service=bool(config.get("home_service", False)),
        home_service_fee_kobo=int(config.get("home_service_fee_kobo", 0)),
    )


def _locate(data: dict[str, Any]) -> None:
    """Stores coordinates for the business's address (or area) in its workspace data."""
    full = ", ".join(p for p in (data.get("address"), data.get("area")) if p)
    point = geo.geocode(full) or geo.geocode(data.get("area", ""))
    data.pop("lat", None)
    data.pop("lng", None)
    if point:
        data["lat"], data["lng"] = point


def update_profile(session: Session, business: Business, **changes: Any) -> None:
    """Sets name/about/category/area/address/whatsapp on the business's workspace."""
    workspace = business.workspace
    if name := changes.pop("name", None):
        workspace.name = name
    if (about := changes.pop("about", None)) is not None:
        workspace.description = about.strip()
    data = dict(workspace.data or {})
    moved = any(changes.get(k) is not None and changes[k] != data.get(k) for k in ("address", "area"))
    data.update({k: v for k, v in changes.items() if v is not None})
    if moved:
        _locate(data)
    workspace.data = data
    session.add(workspace)


def create_business(
    session: Session,
    owner: Account,
    name: str,
    category: str = "",
    area: str = "",
    address: str = "",
    about: str = "",
    whatsapp: str = "",
    location: geo.Point | None = None,
    deposit_kobo: int | None = None,
    home_service_fee_kobo: int | None = None,
    policies: list[str] | None = None,
    hours: list[tuple[int, time, time]] | None = None,
) -> Business:
    tenant = tenant_action.ensure_default_tenant(session, settings=settings.scope("TENANCY"), commit=False)
    data: dict[str, Any] = {
        "category": category,
        "area": area,
        "address": address,
        "whatsapp": whatsapp,
        "ref_prefix": _ref_prefix(name),
        "next_ref": FIRST_REF,
    }
    if location:
        data["lat"], data["lng"] = location
    else:
        _locate(data)
    workspace = workspace_action.create_with_owner(
        session,
        data=WorkspaceCreate(
            name=name,
            slug=profile_slug(name, area),
            description=about.strip(),
            owner_id=owner.id,
            status=WorkspaceStatus.open,
            logo_url=photo_url(name),
            data=data,
        ),
        owner=owner,
        tenant=tenant,
        commit=False,
    )
    user_action.create_membership(
        session, account_id=owner.id, workspace_id=workspace.id, owner_id=owner.id, commit=False
    )
    owner.current_workspace_id = workspace.id
    session.add(owner)
    hours = hours if hours is not None else [(day, time(9), time(18)) for day in range(6)]
    save_booking_config(
        session,
        workspace.id,
        deposit_kobo=settings.DEFAULT_DEPOSIT_NAIRA * 100 if deposit_kobo is None else deposit_kobo,
        deposit_defaulted=True,
        home_service=home_service_fee_kobo is not None,
        home_service_fee_kobo=home_service_fee_kobo or 0,
        policies=policies or [],
        hours=hours_to_config(hours),
    )
    return load_business(session, workspace)


def business_by_slug(session: Session, slug: str) -> Business:
    workspace = workspace_action.get_by_all(session, slug=slug)
    if workspace is None:
        raise NotFound(f"No business called '{slug}'. Use find_businesses to look it up.")
    return load_business(session, workspace)


def business_by_id(session: Session, workspace_id: int) -> Business:
    workspace = workspace_action.get(session, workspace_id)
    if workspace is None:
        raise NotFound("Business not found.")
    return load_business(session, workspace)


def business_for_account(session: Session, account: Account) -> Business | None:
    """The business an owner or staff member is working in (their current workspace)."""
    memberships = user_action.get_multi_by_all(session, account_id=account.id, limit=None)
    if not memberships:
        return None
    ids = [m.workspace_id for m in memberships]
    workspace_id = account.current_workspace_id if account.current_workspace_id in ids else ids[0]
    return business_by_id(session, workspace_id)


def team_accounts(session: Session, business: Business) -> list[Account]:
    """Owner and admin members, who get notified about the business."""
    stmt = select(User).where(
        User.workspace_id == business.id, col(User.type).in_([UserType.owner, UserType.admin])
    )
    return [account_action.get(session, m.account_id) for m in session.exec(stmt)]


def apply_default_deposit(session: Session) -> None:
    """Businesses created before DEFAULT_DEPOSIT_NAIRA get it once; an owner's later choice (even 0) sticks."""
    for workspace in session.exec(select(Workspace).order_by(Workspace.id)):
        config = booking_config(session, workspace.id)
        if config.get("deposit_defaulted"):
            continue
        changes: dict[str, Any] = {"deposit_defaulted": True}
        if not int(config.get("deposit_kobo", 0)):
            changes["deposit_kobo"] = settings.DEFAULT_DEPOSIT_NAIRA * 100
        save_booking_config(session, workspace.id, **changes)
    session.commit()


def open_businesses(session: Session) -> list[Business]:
    return [
        load_business(session, workspace)
        for workspace in session.exec(
            select(Workspace).where(Workspace.status == WorkspaceStatus.open).order_by(Workspace.id)
        )
    ]


# Services


def list_services(
    session: Session, business: Business, query: str | None = None, published_only: bool = True
) -> list[Service]:
    stmt = select(Service).where(Service.workspace_id == business.id).order_by(Service.id)
    if published_only:
        stmt = stmt.where(Service.is_published == True)  # noqa: E712
    services = list(session.exec(stmt))
    if query:
        words = keywords(query)
        services = [s for s in services if words & keywords(f"{s.name} {s.description}")]
    return services


def add_service(
    session: Session,
    business: Business,
    name: str,
    price_kobo: int,
    duration_min: int,
    description: str = "",
    is_published: bool = True,
) -> Service:
    return service_action.create(
        session,
        data=ServiceCreate(
            workspace_id=business.id,
            name=name,
            description=description,
            price_kobo=price_kobo,
            duration_min=duration_min,
            is_published=is_published,
        ),
        commit=False,
    )


def get_service(session: Session, business: Business, service_id: int) -> Service:
    service = service_action.get(session, service_id)
    if service is None or service.workspace_id != business.id:
        raise NotFound(f"No service {service_id} at {business.name}. Use list_services to see the menu.")
    return service


MAX_SERVICE_PHOTOS = 6


def set_service_photos(session: Session, business: Business, service_id: int, photo_urls: list[str]) -> Service:
    service = get_service(session, business, service_id)
    service.photo_urls = photo_urls[:MAX_SERVICE_PHOTOS]
    session.add(service)
    return service


def update_service(session: Session, business: Business, service_id: int, **changes: Any) -> Service:
    service = get_service(session, business, service_id)
    return service_action.update(
        session,
        model=service,
        update={k: v for k, v in changes.items() if v is not None},
        commit=False,
    )


# Customers


def customer_account(session: Session, name: str, phone: str, email: str | None = None) -> Account:
    """The customer's MSFLib account, found by phone or email, or created without a usable password."""
    stored_phone = account_phone(phone)
    email = email.lower() if email else None
    account = account_action.get_by_all(session, phone=stored_phone)
    if account is None and email:
        account = account_action.get_by_email(session, email=email)
    if account is None:
        return account_action.create(
            session,
            data=AccountCreate(
                email=email or f"{phone_key(phone)}@{CUSTOMER_EMAIL_DOMAIN}",
                phone=stored_phone,
                password=secrets.token_urlsafe(24),
                data={"kind": "customer"},
                profile=profile_for(name),
            ),
            commit=False,
        )
    if email and account.email.endswith(f"@{CUSTOMER_EMAIL_DOMAIN}"):
        if account_action.get_by_email(session, email=email) is None:
            account.email = email
            session.add(account)
    return account


def upsert_customer(
    session: Session,
    business: Business,
    name: str,
    phone: str,
    email: str | None = None,
    source: str = "chat",
) -> Customer:
    """Finds the business's customer by phone number, creating or updating their details."""
    key = phone_key(phone)
    if len(key) < 7:
        raise BookingError("Please give a valid phone number.")
    customer = customer_action.get_by_all(session, workspace_id=business.id, phone_key=key)
    if customer is None:
        account = customer_account(session, name, phone, email)
        return customer_action.create(
            session,
            data=CustomerCreate(
                workspace_id=business.id,
                account_id=account.id,
                name=name,
                phone=phone,
                phone_key=key,
                email=email,
                source=source,
            ),
            commit=False,
        )
    customer.name = name or customer.name
    customer.phone = phone
    customer.email = email or customer.email
    customer.last_seen_at = utcnow()
    session.add(customer)
    session.flush()
    return customer


def list_customers(session: Session, business: Business, query: str | None = None) -> list[Customer]:
    stmt = (
        select(Customer)
        .where(Customer.workspace_id == business.id)
        .order_by(col(Customer.last_seen_at).desc())
    )
    if query:
        like = f"%{query.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Customer.name).like(like),
                func.lower(func.coalesce(Customer.email, "")).like(like),
                col(Customer.phone_key).like(f"%{phone_key(query) or query}%"),
            )
        )
    return list(session.exec(stmt))


def get_customer(session: Session, business: Business, customer_id: int) -> Customer:
    customer = customer_action.get(session, customer_id)
    if customer is None or customer.workspace_id != business.id:
        raise NotFound("Customer not found.")
    return customer


# Availability and bookings


def expire_holds(session: Session) -> None:
    session.execute(
        update(Booking)
        .where(Booking.status == "held", col(Booking.hold_expires_at) <= utcnow())
        .values(status="expired")
    )


def _busy(session: Session, business: Business, start: datetime, end: datetime, skip: int | None = None):
    bookings = session.exec(
        select(Booking).where(
            Booking.workspace_id == business.id,
            col(Booking.status).in_(ACTIVE),
            Booking.start < end,
            Booking.end > start,
        )
    )
    busy = [(b.start, b.end) for b in bookings if b.id != skip]
    blocks = session.exec(
        select(BlockedSlot).where(
            BlockedSlot.workspace_id == business.id, BlockedSlot.start < end, BlockedSlot.end > start
        )
    )
    return busy + [(b.start, b.end) for b in blocks]


def free_start_times(session: Session, business: Business, service: Service, day: date) -> list[datetime]:
    expire_holds(session)
    day_start = datetime.combine(day, time(0), LAGOS)
    busy = _busy(session, business, day_start, day_start + timedelta(days=1))
    length = timedelta(minutes=service.duration_min)
    current = utcnow()
    free = []
    for weekday, opens, closes in business.hours:
        if weekday != day.weekday():
            continue
        start = datetime.combine(day, opens, LAGOS)
        close = datetime.combine(day, closes, LAGOS)
        while start + length <= close:
            end = start + length
            if start > current and not any(s < end and start < e for s, e in busy):
                free.append(start)
            start += SLOT_STEP
    return free


def _next_ref(session: Session, business: Business) -> str:
    workspace = business.workspace
    data = dict(workspace.data or {})
    number = int(data.get("next_ref", FIRST_REF))
    data["next_ref"] = number + 1
    workspace.data = data
    session.add(workspace)
    return f"{business.ref_prefix}-{number:04d}"


def create_booking(
    session: Session,
    business: Business,
    service_id: int,
    start: datetime,
    name: str,
    phone: str,
    email: str | None = None,
    notes: str = "",
) -> Booking:
    service = get_service(session, business, service_id)
    if not service.is_published:
        raise NotFound(f"{service.name} is not available to book.")
    if start.tzinfo is None:
        start = start.replace(tzinfo=LAGOS)
    if start not in free_start_times(session, business, service, start.astimezone(LAGOS).date()):
        raise BookingError("That time is not available. Use check_availability to see free times.")

    customer = upsert_customer(session, business, name, phone, email)
    deposit = min(business.deposit_kobo, service.price_kobo)
    return booking_action.create(
        session,
        data=BookingCreate(
            ref=_next_ref(session, business),
            workspace_id=business.id,
            service_id=service.id,
            customer_id=customer.id,
            service_name=service.name,
            start=start,
            end=start + timedelta(minutes=service.duration_min),
            notes=notes,
            total_kobo=service.price_kobo,
            deposit_kobo=deposit,
            status="held" if deposit else "confirmed",
            hold_expires_at=utcnow() + timedelta(minutes=settings.HOLD_MINUTES) if deposit else None,
        ),
        commit=False,
    )


def booking_by_ref(session: Session, ref: str) -> Booking:
    expire_holds(session)
    booking = booking_action.get_by_all(session, ref=ref.strip().upper())
    if booking is None:
        raise NotFound(f"No booking with ref {ref}.")
    return booking


def get_booking(session: Session, ref: str, phone: str) -> Booking:
    booking = booking_by_ref(session, ref)
    if booking.customer.phone_key != phone_key(phone):
        raise NotFound(f"No booking with ref {ref} for that phone number.")
    return booking


def business_booking(session: Session, business: Business, ref: str) -> Booking:
    booking = booking_by_ref(session, ref)
    if booking.workspace_id != business.id:
        raise NotFound(f"No booking with ref {ref}.")
    return booking


def confirm_booking(session: Session, booking: Booking) -> Booking:
    """Marks a booking confirmed once its deposit is in. A lapsed hold is kept if the slot is still free."""
    if booking.status == "confirmed":
        return booking
    if booking.status == "cancelled":
        raise BookingError("This booking was cancelled.")
    if booking.status == "expired":
        business = business_by_id(session, booking.workspace_id)
        if _busy(session, business, booking.start, booking.end, skip=booking.id):
            raise BookingError("This hold expired and the slot was taken. Please book again.")
    booking.status = "confirmed"
    session.add(booking)
    session.flush()
    return booking


def list_bookings(
    session: Session, business: Business, day: date | None = None, status: str | None = None
) -> list[Booking]:
    expire_holds(session)
    stmt = select(Booking).where(Booking.workspace_id == business.id).order_by(Booking.start)
    if day is not None:
        start = datetime.combine(day, time(0), LAGOS)
        stmt = stmt.where(Booking.start >= start, Booking.start < start + timedelta(days=1))
    if status:
        stmt = stmt.where(Booking.status == status)
    return list(session.exec(stmt))


def cancel_booking(session: Session, business: Business, ref: str) -> Booking:
    booking = business_booking(session, business, ref)
    booking.status = "cancelled"
    session.add(booking)
    session.flush()
    return booking


def block_dates(
    session: Session, business: Business, start_day: date, end_day: date, reason: str = ""
) -> list[Booking]:
    """Blocks whole days and returns active bookings that clash with the block."""
    if end_day < start_day:
        raise BookingError("end_date must be on or after start_date.")
    start = datetime.combine(start_day, time(0), LAGOS)
    end = datetime.combine(end_day + timedelta(days=1), time(0), LAGOS)
    clashes = [
        b for b in list_bookings(session, business) if b.status in ACTIVE and b.start < end and start < b.end
    ]
    blocked_slot_action.create(
        session,
        data=BlockedSlotCreate(workspace_id=business.id, start=start, end=end, reason=reason),
        commit=False,
    )
    return clashes


# Questions, call logs and insights


def answer_question(session: Session, business: Business, question: str) -> list[tuple[str, str]]:
    """Facts from the business's own data that match the question."""
    facts = [(policy, "policies") for policy in business.policies] + [
        (
            f"{s.name}: {naira(s.price_kobo)}, about {duration_label(s.duration_min)}"
            + (f". {s.description}" if s.description else ""),
            "price list",
        )
        for s in list_services(session, business)
    ]
    words = keywords(question)
    scored = sorted(
        ((len(words & keywords(text)), text, source) for text, source in facts),
        key=lambda item: item[0],
        reverse=True,
    )
    return [(text, source) for score, text, source in scored if score > 0][:3]


def open_enquiry(
    session: Session, business: Business, question: str, customer: Customer | None
) -> Enquiry:
    return enquiry_action.create(
        session,
        data=EnquiryCreate(
            workspace_id=business.id, customer_id=customer.id if customer else None, question=question
        ),
        commit=False,
    )


def log_call(
    session: Session,
    server: str,
    tool: str,
    workspace_id: int | None,
    arguments: dict[str, Any],
    status: str,
    duration_ms: int,
) -> None:
    call_log_action.create(
        session,
        data=McpCallLogCreate(
            workspace_id=workspace_id,
            server=server,
            tool=tool,
            arguments=arguments,
            status=status,
            duration_ms=duration_ms,
        ),
        commit=False,
    )


def insights(session: Session, business: Business) -> dict[str, Any]:
    logs = list(
        session.exec(
            select(McpCallLog).where(McpCallLog.workspace_id == business.id, McpCallLog.server == "customer")
        )
    )
    service_names = {s.id: s.name for s in list_services(session, business, published_only=False)}
    services_asked: Counter[str] = Counter()
    days_asked: Counter[str] = Counter()
    for log in logs:
        if (service_id := log.arguments.get("service_id")) is not None:
            if name := service_names.get(int(service_id)):
                services_asked[name] += 1
        if requested := log.arguments.get("date"):
            try:
                days_asked[WEEKDAYS[date.fromisoformat(str(requested)).weekday()]] += 1
            except ValueError:
                pass
    bookings = list_bookings(session, business)
    open_enquiries = session.exec(
        select(Enquiry).where(Enquiry.workspace_id == business.id, Enquiry.status == "open")
    )
    return {
        "customer_tool_calls": len(logs),
        "tool_usage": dict(Counter(log.tool for log in logs).most_common()),
        "most_asked_services": dict(services_asked.most_common(5)),
        "days_customers_asked_about": dict(days_asked.most_common()),
        "bookings_by_status": dict(Counter(b.status for b in bookings)),
        "deposits_collected": naira(sum(b.deposit_kobo for b in bookings if b.status == "confirmed")),
        "open_questions": [e.question for e in open_enquiries],
    }
