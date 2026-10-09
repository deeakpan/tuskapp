import hashlib
import hmac
import json
from contextlib import AsyncExitStack, asynccontextmanager
from html import escape
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from msflib.eventbus import bind_app_emitter
from sqlmodel import SQLModel

from tusk_mcp import listeners  # noqa: F401  (registers event listeners before the emitter is bound)
from tusk_mcp import models  # noqa: F401  (registers tables)
from tusk_mcp.api.router import api_router
from tusk_mcp.core.config import settings
from tusk_mcp.db.session import engine, session_scope
from tusk_mcp.seed import seed_demo
from tusk_mcp.servers import customer, owner
from tusk_mcp.services import business as biz
from tusk_mcp.services.business import BookingError, NotFound, booking_by_ref, naira, when_label
from tusk_mcp.services.chats import record_chat
from tusk_mcp.services.payments import complete_payment, is_test_checkout, payment_by_reference

customer_app = customer.mcp.streamable_http_app()
owner_app = owner.mcp.streamable_http_app()


def create_tables() -> None:
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    with session_scope() as session:
        if settings.SEED_DEMO:
            seed_demo(session)
        biz.apply_default_deposit(session)
    async with AsyncExitStack() as stack:
        await stack.enter_async_context(customer.mcp.session_manager.run())
        await stack.enter_async_context(owner.mcp.session_manager.run())
        yield


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)
bind_app_emitter(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin).rstrip("/") for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.API_V1_STR)
app.mount("/mcp/customer", customer_app)
app.mount("/mcp/owner", owner_app)
if settings.STORAGE_METHOD == "file":
    # MSFLib's local storage writes to STORAGE_PATH; cloud methods (s3, cloudinary...) serve their own URLs.
    Path(settings.STORAGE_PATH).mkdir(parents=True, exist_ok=True)
    app.mount(settings.STORAGE_BASE_URL, StaticFiles(directory=settings.STORAGE_PATH), name="uploads")


@app.exception_handler(NotFound)
async def not_found(request: Request, exc: NotFound) -> JSONResponse:
    return JSONResponse({"detail": str(exc)}, status_code=404)


@app.exception_handler(BookingError)
async def booking_error(request: Request, exc: BookingError) -> JSONResponse:
    return JSONResponse({"detail": str(exc)}, status_code=400)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def _page(title: str, body: str, status_code: int = 200) -> HTMLResponse:
    return HTMLResponse(
        "<!doctype html><meta name=viewport content='width=device-width,initial-scale=1'>"
        f"<title>{escape(title)}</title>"
        "<body style='font-family:system-ui;max-width:28rem;margin:4rem auto;padding:0 1rem;line-height:1.5'>"
        f"<h1>{escape(title)}</h1>{body}</body>",
        status_code=status_code,
    )


@app.get("/pay/test/{reference}", response_class=HTMLResponse)
def test_checkout(reference: str) -> HTMLResponse:
    """Stands in for the Paystack checkout page when PAYSTACK_SECRET_KEY isn't set."""
    with session_scope() as session:
        try:
            payment = payment_by_reference(session, reference)
        except NotFound:
            return _page("Payment not found", "<p>This payment link is not valid.</p>", 404)
        if not is_test_checkout(payment):
            return _page("Payment not found", "<p>This payment link is not valid.</p>", 404)
        description, amount = payment.description or "Deposit", naira(round(payment.amount * 100))
    return _page(
        "Test checkout",
        f"<p>{escape(description)}</p><p style='font-size:2rem;margin:.5rem 0'><b>{amount}</b></p>"
        "<p style='color:#666'>Test mode: no money moves. Set PAYSTACK_SECRET_KEY to use Paystack.</p>"
        f"<form action='/pay/complete' method='get'><input type=hidden name=reference value='{escape(reference)}'>"
        "<button style='font-size:1rem;padding:.75rem 1.5rem'>Pay now</button></form>",
    )


@app.get("/pay/complete", response_class=HTMLResponse)
async def pay_complete(reference: str) -> HTMLResponse:
    """Paystack's callback (and the test checkout's): verify, then confirm the booking via the payment queue."""
    with session_scope() as session:
        try:
            payment, fulfilled = await complete_payment(session, reference)
            booking = booking_by_ref(session, (payment.queue.data or {})["booking_ref"])
        except (NotFound, BookingError) as exc:
            return _page("Payment not completed", f"<p>{escape(str(exc))}</p>", 400)
        message = (
            f"Deposit of {naira(booking.deposit_kobo)} received. Booking {booking.ref} for "
            f"{booking.service_name}, {when_label(booking.start)} is confirmed."
        )
        chat = (booking.workspace_id, booking.customer_id)
    if fulfilled:
        record_chat(*chat, [("assistant", message)])
    return _page("Deposit paid", f"<p>{escape(message)}</p><p>You can go back to the chat.</p>")


@app.post("/pay/webhook")
async def paystack_webhook(request: Request) -> JSONResponse:
    """Paystack's server-to-server notice, so a deposit confirms even if the customer closes the tab.

    Set this URL (PUBLIC_BASE_URL/pay/webhook) under Paystack → Settings → API Keys & Webhooks.
    """
    body = await request.body()
    secret = settings.PAYSTACK_SECRET_KEY.encode()
    expected = hmac.new(secret, body, hashlib.sha512).hexdigest()
    if not secret or not hmac.compare_digest(expected, request.headers.get("x-paystack-signature", "")):
        return JSONResponse({"detail": "Invalid signature"}, status_code=401)
    event = json.loads(body)
    reference = (event.get("data") or {}).get("reference")
    if event.get("event") != "charge.success" or not reference:
        return JSONResponse({"status": "ignored"})
    with session_scope() as session:
        try:
            payment, fulfilled = await complete_payment(session, reference)
            booking = booking_by_ref(session, (payment.queue.data or {})["booking_ref"])
        except (NotFound, BookingError) as exc:
            # 200 so Paystack doesn't retry a payment we can't match; it's logged on the payment instead.
            return JSONResponse({"status": "not processed", "detail": str(exc)})
        chat = (booking.workspace_id, booking.customer_id)
        message = f"Deposit received. Booking {booking.ref} is confirmed."
    if fulfilled:
        record_chat(*chat, [("assistant", message)])
    return JSONResponse({"status": "ok"})


def main() -> None:
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)


if __name__ == "__main__":
    main()
