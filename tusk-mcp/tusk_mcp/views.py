from datetime import datetime
from typing import Any

from tusk_mcp.models import Account, Booking, Customer, Enquiry, Payment, Service
from tusk_mcp.services.business import (
    LAGOS,
    WEEKDAYS,
    Business,
    duration_label,
    full_name,
    media_url,
    naira,
    time_label,
)


def iso(value: datetime | None) -> str | None:
    return value.isoformat() if value else None


def business_summary(business: Business) -> dict[str, Any]:
    return {
        "slug": business.slug,
        "name": business.name,
        "category": business.category,
        "area": business.area,
        "about": business.about,
        "profile_url": business.profile_url,
        "cover_photo": business.cover_photo,
    }


def business_detail(business: Business) -> dict[str, Any]:
    return {
        **business_summary(business),
        "address": business.address,
        "whatsapp_url": business.whatsapp_url(f"Hi {business.name}, I found you on TuskApp."),
        "opening_hours": [
            f"{WEEKDAYS[day]} {time_label(opens)}–{time_label(closes)}" for day, opens, closes in business.hours
        ],
        "deposit_to_book": naira(business.deposit_kobo) if business.deposit_kobo else None,
        "home_service": {
            "offered": business.home_service,
            "fee": naira(business.home_service_fee_kobo) if business.home_service else None,
        },
        "policies": business.policies,
    }


def service_card(service: Service) -> dict[str, Any]:
    return {
        "id": service.id,
        "name": service.name,
        "description": service.description,
        "price": naira(service.price_kobo),
        "price_kobo": service.price_kobo,
        "duration": duration_label(service.duration_min),
        "duration_min": service.duration_min,
        "photo_urls": [media_url(url) for url in service.photo_urls],
        "is_published": service.is_published,
    }


def booking_detail(booking: Booking, payment: Payment | None = None) -> dict[str, Any]:
    start = booking.start.astimezone(LAGOS)
    customer = booking.customer
    detail = {
        "ref": booking.ref,
        "status": booking.status,
        "service": booking.service_name,
        "when": f"{start:%a %d %b}, {time_label(start)}",
        "start_time": start.isoformat(),
        "customer_name": customer.name,
        "customer_phone": customer.phone,
        "customer_email": customer.email,
        "notes": booking.notes,
        "total": naira(booking.total_kobo),
        "total_kobo": booking.total_kobo,
        "deposit": naira(booking.deposit_kobo),
        "deposit_kobo": booking.deposit_kobo,
        "hold_expires_at": iso(booking.hold_expires_at),
        "created_at": iso(booking.booked_at),
    }
    if payment is not None:
        detail["payment"] = {
            "reference": payment.reference,
            "status": payment.status,
            "gateway": payment.gateway,
            "pay_url": payment.authorization_url,
        }
    return detail


def customer_detail(customer: Customer) -> dict[str, Any]:
    bookings = customer.bookings
    paid = [b for b in bookings if b.status == "confirmed"]
    return {
        "id": customer.id,
        "name": customer.name,
        "phone": customer.phone,
        "email": customer.email,
        "source": customer.source,
        "bookings": len(bookings),
        "confirmed_bookings": len(paid),
        "total_value": naira(sum(b.total_kobo for b in paid)),
        "first_seen": iso(customer.first_seen_at),
        "last_seen": iso(customer.last_seen_at),
        "has_chat": customer.conversation_id is not None,
    }


def enquiry_detail(enquiry: Enquiry) -> dict[str, Any]:
    customer = enquiry.customer
    return {
        "id": enquiry.id,
        "question": enquiry.question,
        "answer": enquiry.answer,
        "status": enquiry.status,
        "customer_name": customer.name if customer else None,
        "customer_phone": customer.phone if customer else None,
        "customer_email": customer.email if customer else None,
        "created_at": iso(enquiry.asked_at),
    }


def user_detail(account: Account) -> dict[str, Any]:
    return {"id": account.id, "name": full_name(account), "email": account.email, "phone": account.phone}
