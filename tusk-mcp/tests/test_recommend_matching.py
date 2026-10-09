"""Owners write services and categories their own way; customers' wording should still find them."""

from fastapi.testclient import TestClient

from tests.conftest import login
from tests.mcp_client import call_tool


def test_gadget_store_found_for_phone_search(client: TestClient) -> None:
    signup = client.post(
        "/api/v1/auth/signup",
        json={
            "name": "Gift Udo",
            "email": "giddy@example.com",
            "phone": "0809 333 4444",
            "password": "giddy-password-1",
            "business_name": "Giddy Gadget",
            "category": "Gadgets Store",
            "area": "Calabar",
            "about": "Multi device store for phones, laptops and accessories. Brand new, UK and Nigerian used.",
        },
    )
    assert signup.status_code == 201, signup.text
    headers = login(client, "giddy@example.com", "giddy-password-1")
    created = client.post(
        "/api/v1/services",
        json={"name": "Uk used Iphone 13pro", "price_naira": 456_000, "duration_min": 30},
        headers=headers,
    )
    assert created.status_code == 201, created.text

    for args in (
        {"need": "UK-used iPhone 13 Pro", "category": "phones"},
        {"need": "iphone 13 pro"},
        {"need": "iPhone 13 Pro 128GB", "category": "phone shop"},
    ):
        names = [o["name"] for o in call_tool(client, "customer", "find_businesses", args)["options"]]
        assert "Giddy Gadget" in names, (args, names)
