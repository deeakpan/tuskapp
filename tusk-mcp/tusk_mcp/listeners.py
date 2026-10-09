"""Event bus listeners. Import before `bind_app_emitter(app)` so they're bound to the app emitter."""

from typing import Any

from msflib.eventbus import listen
from msflib.payments.models import PaymentQueue

from tusk_mcp.services.business import booking_by_ref, business_by_id, confirm_booking, naira, when_label
from tusk_mcp.services.notify import notify_new_order
from tusk_mcp.services.payments import DEPOSIT_EVENT_KEY


@listen(f"payment-queue-execute-{DEPOSIT_EVENT_KEY}")
def confirm_paid_booking(queue: PaymentQueue, payload: dict[str, Any]) -> None:
    session = payload["session"]
    booking = confirm_booking(session, booking_by_ref(session, queue.data["booking_ref"]))
    business = business_by_id(session, booking.workspace_id)
    notify_new_order(
        session,
        business,
        f"{booking.customer.name} paid the {naira(booking.deposit_kobo)} deposit for "
        f"{booking.service_name}, {when_label(booking.start)}. Ref {booking.ref}.",
    )
