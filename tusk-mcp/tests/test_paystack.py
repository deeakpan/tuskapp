"""The real Paystack path: MSFLib's PaystackGateway runs for real; only Paystack's HTTP API is faked."""

import hashlib
import hmac
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from tests.conftest import login
from tests.mcp_client import call_tool
from tests.test_booking_flow import book_cornrows
from tusk_mcp.core.config import settings
from msflib.payments.service import paystack_gateway

SECRET = "sk_test_fake_for_tests"
REFERENCE = "psk_ref_0001"


@pytest.fixture
def paystack(monkeypatch: pytest.MonkeyPatch) -> list[httpx.Request]:
    calls: list[httpx.Request] = []
    deposit_kobo = 500_000

    def fake_api(request: httpx.Request) -> httpx.Response:
        calls.append(request)
        assert request.headers["Authorization"] == f"Bearer {SECRET}"
        if request.url.path == "/transaction/initialize":
            body = json.loads(request.content)
            assert body["amount"] == deposit_kobo
            data = {"authorization_url": "https://checkout.paystack.com/abc123", "access_code": "abc123",
                    "reference": REFERENCE}
            return httpx.Response(200, json={"status": True, "data": data})
        if request.url.path == f"/transaction/verify/{REFERENCE}":
            data = {"status": "success", "reference": REFERENCE, "amount": deposit_kobo, "currency": "NGN"}
            return httpx.Response(200, json={"status": True, "data": data})
        return httpx.Response(404, json={"status": False})

    real_client = httpx.AsyncClient
    monkeypatch.setattr(
        paystack_gateway.httpx, "AsyncClient",
        lambda **kwargs: real_client(transport=httpx.MockTransport(fake_api), **kwargs),
    )
    monkeypatch.setattr(settings, "PAYSTACK_SECRET_KEY", SECRET)
    scoped = settings.scope("PAYMENTS")
    if scoped is not settings:
        monkeypatch.setattr(scoped, "PAYSTACK_SECRET_KEY", SECRET)
    return calls


def signed(body: dict) -> tuple[bytes, dict[str, str]]:
    raw = json.dumps(body).encode()
    return raw, {"x-paystack-signature": hmac.new(SECRET.encode(), raw, hashlib.sha512).hexdigest(),
                 "content-type": "application/json"}


def test_paystack_deposit_confirms_by_webhook(client: TestClient, paystack: list[httpx.Request]) -> None:
    booking = book_cornrows(client, "08035550909")
    assert booking["status"] == "held"
    assert booking["pay_url"] == "https://checkout.paystack.com/abc123"
    assert booking["payment"]["reference"] == REFERENCE

    raw, headers = signed({"event": "charge.success", "data": {"reference": REFERENCE}})
    forged = client.post("/pay/webhook", content=raw, headers={**headers, "x-paystack-signature": "bad"})
    assert forged.status_code == 401

    assert client.post("/pay/webhook", content=raw, headers=headers).json() == {"status": "ok"}
    status = call_tool(client, "customer", "get_booking", {"ref": booking["ref"], "phone": "08035550909"})
    assert status["status"] == "confirmed"
    assert [c.url.path for c in paystack] == ["/transaction/initialize", f"/transaction/verify/{REFERENCE}"]

    # Paystack retries webhooks and the customer may also land on the callback: both are no-ops now.
    assert client.post("/pay/webhook", content=raw, headers=headers).json() == {"status": "ok"}
    assert client.get("/pay/complete", params={"reference": REFERENCE}).status_code == 200
    assert len(paystack) == 2

    bookings = client.get("/api/v1/bookings", headers=login(client, "tolu@tuskapp.demo")).json()
    paid = next(b for b in bookings if b["ref"] == booking["ref"])
    assert paid["status"] == "confirmed"
