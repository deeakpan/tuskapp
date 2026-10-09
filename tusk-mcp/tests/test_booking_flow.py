"""A customer books through the Customer MCP, pays the deposit, and the owner sees it all on the dashboard."""

from datetime import datetime, timedelta
from urllib.parse import urlsplit

import pytest
from fastapi.testclient import TestClient

from tests.conftest import login
from tests.mcp_client import ToolFailed, call_tool
from tusk_mcp.services import geo
from tusk_mcp.services.business import LAGOS


def next_tuesday() -> str:
    today = datetime.now(LAGOS).date()
    return str(today + timedelta(days=(1 - today.weekday()) % 7 or 7))


def book_cornrows(client: TestClient, phone: str, email: str | None = "chioma@example.com") -> dict:
    services = call_tool(client, "customer", "list_services", {"slug": "glam-by-tolu", "query": "cornrows"})
    cornrows = services[0]
    slots = call_tool(
        client, "customer", "check_availability", {"slug": "glam-by-tolu", "service_id": cornrows["id"], "date": next_tuesday()}
    )
    start = slots["free_start_times"][0]["start_time"]
    return call_tool(
        client,
        "customer",
        "create_booking",
        {
            "slug": "glam-by-tolu",
            "service_id": cornrows["id"],
            "start_time": start,
            "name": "Chioma Eze",
            "phone": phone,
            "email": email,
        },
    )


def slugs(result: dict) -> list[str]:
    return [option["slug"] for option in result["options"]]


def test_discovery(client: TestClient) -> None:
    found = call_tool(client, "customer", "find_businesses", {"need": "knotless braids"})
    assert slugs(found) == ["glam-by-tolu"]
    assert "brides" in found["options"][0]["about"]
    office = call_tool(client, "customer", "find_businesses", {"need": "lunch trays for the office"})
    assert slugs(office) == ["mama-put-kitchen"]
    # Casual conversation: no shared words, but the inferred category still finds the right business.
    casual = call_tool(
        client, "customer", "find_businesses", {"need": "something nice for my sister's wedding", "category": "hair salon"}
    )
    assert slugs(casual) == ["glam-by-tolu"]
    assert casual["notes"]
    assert slugs(call_tool(client, "customer", "find_businesses", {"category": "phone shop"}))[0] in {
        "gadget-hub-uyo", "anyi-gadgets", "paul-phones", "charles-mobile"
    }
    detail = call_tool(client, "customer", "get_business", query="?b=glam-by-tolu")
    assert detail["deposit_to_book"] == "₦5,000"
    assert detail["whatsapp_url"].startswith("https://wa.me/2348030000001?text=")
    contact = call_tool(
        client, "customer", "contact_business", {"slug": "glam-by-tolu", "reason": "Change my time", "ref": "gbt-0412"}
    )
    assert "booking%20GBT-0412" in contact["whatsapp_url"]
    assert contact["phone"] == "0803 000 0001" and contact["owner_alerted"] is False

    contact = call_tool(
        client,
        "customer",
        "contact_business",
        {"slug": "glam-by-tolu", "reason": "Can you do my braids at home?", "name": "Ime", "phone": "0803 123 4567"},
    )
    assert contact["owner_alerted"] is True
    tolu = login(client, "tolu@tuskapp.demo")
    alerts = client.get("/api/v1/notifications", headers=tolu).json()
    alerts = alerts.get("items", alerts) if isinstance(alerts, dict) else alerts
    assert any("Ime" in a["notification"]["message"] and "0803 123 4567" in a["notification"]["message"] for a in alerts), alerts
    with pytest.raises(ToolFailed, match="Which business"):
        call_tool(client, "customer", "get_business")


ITAM = (5.0650, 7.8700)


def test_recommendations_weigh_distance_price_and_home_service(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(geo, "geocode", lambda text: ITAM if "itam" in text.lower() else None)
    need = {"need": "iPhone 13 Pro 128GB", "near": "Itam, Uyo"}

    result = call_tool(client, "customer", "find_businesses", need)
    options = {o["name"]: o for o in result["options"]}
    assert set(options) == {"Gadget Hub Uyo", "Anyi Gadgets", "Paul Phones", "Charles Mobile"}
    assert options["Anyi Gadgets"]["strengths"][0].startswith("Closest")
    assert options["Anyi Gadgets"]["price_from"] == "₦470,000"
    assert any(s.startswith("Cheapest") for s in options["Paul Phones"]["strengths"])
    assert any(t.startswith("Farthest") for t in options["Paul Phones"]["tradeoffs"])
    assert any(s.startswith("Comes to you") for s in options["Charles Mobile"]["strengths"])
    assert any(t.startswith("Priciest") for t in options["Charles Mobile"]["tradeoffs"])
    assert all(o["summary"] for o in result["options"])

    cheapest_first = call_tool(client, "customer", "find_businesses", {**need, "priority": "cheapest"})
    assert slugs(cheapest_first)[0] == "paul-phones"
    closest_first = call_tool(client, "customer", "find_businesses", {**need, "priority": "closest"})
    assert slugs(closest_first)[0] == "anyi-gadgets"

    delivered = call_tool(client, "customer", "find_businesses", {**need, "home_service": True})
    assert slugs(delivered) == ["charles-mobile"]
    assert delivered["options"][0]["price_from"] == "₦483,000"

    budget = call_tool(client, "customer", "find_businesses", {**need, "budget_naira": 440_000})
    assert slugs(budget)[0] == "paul-phones"
    assert any("budget" in t for t in budget["options"][1]["tradeoffs"])


def test_public_profile(client: TestClient) -> None:
    profile = client.get("/api/v1/public/businesses/anyi-gadgets").json()
    assert profile["name"] == "Anyi Gadgets" and profile["profile_url"].endswith("/anyi-gadgets")
    assert profile["services"][0]["price"]
    assert client.get("/api/v1/public/businesses/nope").status_code == 404
    listed = {b["slug"] for b in client.get("/api/v1/public/businesses").json()}
    assert {"glam-by-tolu", "paul-phones"} <= listed


def test_booking_deposit_payment_confirms_and_notifies(client: TestClient, tolu: dict[str, str]) -> None:
    booking = book_cornrows(client, "0803 555 0101")
    assert booking["status"] == "held"
    assert booking["payment"]["status"] == "unverified"
    pay_url = urlsplit(booking["pay_url"])
    assert pay_url.path.startswith("/pay/test/")

    assert "Test checkout" in client.get(pay_url.path).text
    reference = pay_url.path.rsplit("/", 1)[1]
    paid = client.get("/pay/complete", params={"reference": reference})
    assert paid.status_code == 200 and "Deposit paid" in paid.text

    status = call_tool(client, "customer", "get_booking", {"ref": booking["ref"], "phone": "08035550101"})
    assert status["status"] == "confirmed"

    rows = client.get("/api/v1/bookings", params={"status": "confirmed"}, headers=tolu).json()
    row = next(b for b in rows if b["ref"] == booking["ref"])
    assert row["payment"]["status"] == "verified"

    titles = [n["notification"]["title"] for n in client.get("/api/v1/notifications/", headers=tolu).json()]
    assert "Booking awaiting deposit" in titles and "New booking confirmed" in titles

    customer_id = next(
        c["id"] for c in client.get("/api/v1/customers", params={"q": "chioma"}, headers=tolu).json()
    )
    chat = client.get(f"/api/v1/customers/{customer_id}", headers=tolu).json()["chat"]
    assert chat[0]["from"] == "customer" and "Cornrows" in chat[0]["text"]
    assert any("Deposit of ₦5,000 received" in m["text"] for m in chat)

    # Paystack may call back more than once: no second confirmation message.
    assert client.get("/pay/complete", params={"reference": reference}).status_code == 200
    again = client.get(f"/api/v1/customers/{customer_id}", headers=tolu).json()["chat"]
    assert len(again) == len(chat)


def test_slot_taken_and_unpaid_hold(client: TestClient, tolu: dict[str, str]) -> None:
    held = book_cornrows(client, "0803 555 0202", email=None)
    assert held["status"] == "held"
    confirmed = client.post(f"/api/v1/bookings/{held['ref']}/confirm", headers=tolu).json()
    assert confirmed["status"] == "confirmed"
    cancelled = client.post(f"/api/v1/bookings/{held['ref']}/cancel", headers=tolu).json()
    assert cancelled["status"] == "cancelled"


def test_unanswered_question_goes_to_owner_and_reply_lands_in_chat(client: TestClient, tolu: dict[str, str]) -> None:
    answered = call_tool(
        client, "customer", "ask_business", {"slug": "glam-by-tolu", "question": "Do you do home service?"}
    )
    assert answered["answered"] is True

    unknown = call_tool(
        client,
        "customer",
        "ask_business",
        {"slug": "glam-by-tolu", "question": "Can I bring my own hair extensions?", "name": "Bisi", "phone": "0803 555 0303"},
    )
    assert unknown["answered"] is False
    assert unknown["whatsapp_url"].startswith("https://wa.me/2348030000001")

    open_questions = client.get("/api/v1/enquiries", params={"status": "open"}, headers=tolu).json()
    question = next(q for q in open_questions if "extensions" in q["question"])
    reply = client.post(
        f"/api/v1/enquiries/{question['id']}/answer",
        json={"answer": "Yes, you can bring your own extensions.", "add_to_policies": True},
        headers=tolu,
    )
    assert reply.status_code == 200, reply.text

    customer = next(c for c in client.get("/api/v1/customers", params={"q": "bisi"}, headers=tolu).json())
    chat = client.get(f"/api/v1/customers/{customer['id']}", headers=tolu).json()["chat"]
    assert [m["from"] for m in chat] == ["customer", "assistant", "assistant"]
    assert "replied: Yes, you can bring your own extensions." in chat[-1]["text"]

    again = call_tool(
        client, "customer", "ask_business", {"slug": "glam-by-tolu", "question": "Can I bring extensions?"}
    )
    assert again["answered"] is True
    titles = [n["notification"]["title"] for n in client.get("/api/v1/notifications/", headers=tolu).json()]
    assert "New question" in titles


def test_owner_mcp_tokens(client: TestClient, tolu: dict[str, str]) -> None:
    call_tool(client, "owner", "get_insights", expect_status=401)

    login_token = tolu["Authorization"].split()[1]
    insights = call_tool(client, "owner", "get_insights", token=login_token)
    assert "tool_usage" in insights

    created = client.post("/api/v1/mcp-tokens", json={"name": "Claude"}, headers=tolu).json()
    bookings = call_tool(client, "owner", "list_bookings", token=created["token"])
    assert isinstance(bookings, list)
    listed = client.get("/api/v1/mcp-tokens", headers=tolu).json()
    assert next(t for t in listed if t["id"] == created["id"])["last_used_at"] is not None

    assert client.delete(f"/api/v1/mcp-tokens/{created['id']}", headers=tolu).status_code == 204
    call_tool(client, "owner", "list_bookings", token=created["token"], expect_status=401)

    mama = login(client, "mama@tuskapp.demo")["Authorization"].split()[1]
    customers = call_tool(client, "owner", "list_customers", token=mama)
    assert all("Chioma" not in c["name"] for c in customers)


def test_demo_owner_token(client: TestClient) -> None:
    from tusk_mcp.db.session import session_scope
    from tusk_mcp.seed import demo_owner_token
    from tusk_mcp.services.business import business_by_slug

    with session_scope() as session:
        token = demo_owner_token("glam-by-tolu", business_by_slug(session, "glam-by-tolu").id)
    services_before = call_tool(client, "owner", "update_service", {"service_id": 3, "price_naira": 9000}, token=token)
    assert services_before["price"] == "₦9,000"
