"""Booking deposits through msflib.payments.

With PAYSTACK_SECRET_KEY set, `process_payment` opens a real Paystack (test mode) checkout. Without
it, a local test checkout stands in for Paystack. Both store MSFLib `Payment` and `PaymentQueue`
rows, and both confirm the booking the same way: `/pay/complete` verifies the payment and fires
`payment-queue-execute-booking-deposit`, whose listener confirms the booking.
"""

import secrets

from msflib.eventbus import EventBusListenerExecutionError, EventBusRequiredListenerError, emitter
from msflib.payments.actions import payment_action, payment_queue_action
from msflib.payments.models import (
    Payment,
    PaymentData,
    PaymentGateway,
    PaymentInfo,
    PaymentQueueCreate,
    PaymentQueueStatus,
    PaymentStatus,
)
from msflib.payments.service import PaymentProcessor
from msflib.payments.service.error import PaymentError
from msflib.payments.service.processor import process_payment
from sqlmodel import Session, select

from tusk_mcp.core.config import settings
from tusk_mcp.models import Account, Booking
from tusk_mcp.services.business import Business, BookingError, NotFound

DEPOSIT_EVENT_KEY = "booking-deposit"
DEMO_MODE = "test-checkout"


def paystack_enabled() -> bool:
    return bool(settings.PAYSTACK_SECRET_KEY)


async def start_deposit(session: Session, business: Business, booking: Booking, payer: Account) -> Payment:
    """Creates the deposit payment for a held booking and links it. `payment.authorization_url` is the pay link."""
    data = PaymentData(
        email=payer.email,
        amount=booking.deposit_kobo / 100,
        description=f"{business.name} deposit for {booking.service_name} ({booking.ref})",
        gateway=PaymentGateway.paystack,
        callback_url=f"{settings.PUBLIC_BASE_URL}/pay/complete",
    )
    queue_data = {"booking_ref": booking.ref}
    metadata = {"booking_ref": booking.ref, "workspace_id": business.id}
    if paystack_enabled():
        try:
            payment = await process_payment(
                session,
                payment_data=data,
                account=payer,
                settings=settings,
                queue_event_key=DEPOSIT_EVENT_KEY,
                queue_data=queue_data,
                metadata=metadata,
            )
        except PaymentError as exc:
            raise BookingError(f"Couldn't start the Paystack payment: {exc}") from exc
    else:
        reference = f"tusk_test_{secrets.token_hex(8)}"
        payment = payment_action.create(
            session,
            data=PaymentInfo(
                **data.model_dump(),
                account_id=payer.id,
                authorization_url=f"{settings.PUBLIC_BASE_URL}/pay/test/{reference}",
                access_code=DEMO_MODE,
                reference=reference,
                status=PaymentStatus.unverified,
                data={**metadata, "mode": DEMO_MODE},
            ),
            commit=False,
        )
        payment_queue_action.create(
            session,
            data=PaymentQueueCreate(
                event_key=DEPOSIT_EVENT_KEY, status=PaymentQueueStatus.queued, data=queue_data
            ),
            update={"payment_id": payment.id},
            commit=False,
        )
    payment.queue.entity_id = booking.id
    booking.payment_id = payment.id
    session.add_all([payment.queue, booking])
    session.flush()
    return payment


def payment_by_reference(session: Session, reference: str) -> Payment:
    payment = session.exec(select(Payment).where(Payment.reference == reference)).first()
    if payment is None:
        raise NotFound("Payment not found.")
    return payment


def is_test_checkout(payment: Payment) -> bool:
    return (payment.data or {}).get("mode") == DEMO_MODE


async def complete_payment(session: Session, reference: str) -> tuple[Payment, bool]:
    """Verifies the payment with its gateway, then runs the queued fulfilment (confirming the booking).

    Returns the payment and whether this call fulfilled it (False when it was already done).
    """
    fulfilled = False
    payment = payment_by_reference(session, reference)
    queue = payment.queue
    if payment.status != PaymentStatus.verified:
        processor = PaymentProcessor(settings=settings)
        gateway = processor.gateways[PaymentGateway(payment.gateway)]
        if is_test_checkout(payment):
            verified = {"mode": DEMO_MODE, "amount": gateway.convert_amount(payment.amount)}
        else:
            try:
                result = await processor.gateway(payment.gateway).verify(reference)
            except PaymentError as exc:
                raise BookingError(f"Payment not completed: {exc.cause or exc}") from exc
            if gateway.convert_amount(payment.amount) != result.amount:
                raise BookingError("Payment amount doesn't match the deposit.")
            verified = result.model_dump(mode="json")
        payment.status = PaymentStatus.verified
        payment.data = {**(payment.data or {}), **verified}
        session.add(payment)
        session.commit()

    if queue is not None and queue.status == PaymentQueueStatus.queued:
        try:
            await emitter.emit_required_async(
                f"payment-queue-execute-{queue.event_key}", queue, {"session": session}
            )
        except (EventBusRequiredListenerError, EventBusListenerExecutionError) as exc:
            session.rollback()
            cause = exc.__cause__
            raise BookingError(str(cause) if cause else "Payment received but the booking update failed.") from exc
        queue.status = PaymentQueueStatus.processed
        session.add(queue)
        session.commit()
        fulfilled = True
    session.refresh(payment)
    return payment, fulfilled
