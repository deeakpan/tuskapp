from fastapi.testclient import TestClient

from tests.conftest import login


def test_signup_then_msflib_login_and_logout(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "name": "Ada Obi",
            "email": "Ada@Example.com",
            "phone": "0809 111 2222",
            "password": "ada-password-1",
            "business_name": "Ada's Nails",
            "category": "nails",
            "area": "Lekki, Lagos",
        },
    )
    assert response.status_code == 201, response.text
    signup_headers = {"Authorization": f"Bearer {response.json()['access_token']}"}

    me = client.get("/api/v1/me", headers=signup_headers).json()
    assert me["user"] == {"id": me["user"]["id"], "name": "Ada Obi", "email": "ada@example.com", "phone": "+2348091112222"}
    assert me["business"]["slug"] == "ada-s-nails"
    assert me["business"]["customer_mcp_url"].endswith("/mcp/customer/?b=ada-s-nails")

    duplicate = client.post(
        "/api/v1/auth/signup",
        json={
            "name": "Ada Again",
            "email": "ada@example.com",
            "phone": "0809 000 0000",
            "password": "ada-password-1",
            "business_name": "Other",
        },
    )
    assert duplicate.status_code == 409

    headers = login(client, "ada@example.com", "ada-password-1")
    assert client.get("/api/v1/account/me", headers=headers).json()["email"] == "ada@example.com"
    assert client.delete("/api/v1/logout", headers=headers).status_code == 200
    assert client.get("/api/v1/me", headers=headers).status_code == 401
    assert client.get("/api/v1/me", headers=login(client, "ada@example.com", "ada-password-1")).status_code == 200


def test_wrong_password(client: TestClient) -> None:
    response = client.post("/api/v1/login", data={"username": "tolu@tuskapp.demo", "password": "nope"})
    assert response.status_code == 400


def test_services_crud(client: TestClient, tolu: dict[str, str]) -> None:
    created = client.post(
        "/api/v1/services",
        json={"name": "Pedicure", "price_naira": 6000, "duration_min": 60},
        headers=tolu,
    )
    assert created.status_code == 201, created.text
    service = created.json()
    assert service["price"] == "₦6,000"

    edited = client.patch(f"/api/v1/services/{service['id']}", json={"price_naira": 7000}, headers=tolu).json()
    assert edited["price_kobo"] == 700_000

    assert client.delete(f"/api/v1/services/{service['id']}", headers=tolu).status_code == 204
    names = [s["name"] for s in client.get("/api/v1/services", headers=tolu).json()]
    assert "Pedicure" not in names
    assert "Cornrows" in names


def test_import_price_list_csv(client: TestClient) -> None:
    headers = login(client, "anyi@tuskapp.demo")
    sheet = (
        "Item,Price (₦),Duration,Details,In stock\n"
        "iPhone 13 Pro 128GB (UK used),\"₦470,000\",,Battery 87%,yes\n"
        "Samsung S22 Ultra,380k,45 mins,Clean,yes\n"
        "Old stock iPhone X,150000,,,no\n"
        "AirPods,free,,,yes\n"
        ",9000,,,yes\n"
    )
    imported = client.post(
        "/api/v1/services/import", files={"file": ("prices.csv", sheet.encode(), "text/csv")}, headers=headers
    )
    assert imported.status_code == 200, imported.text
    result = imported.json()
    assert result["updated"] == ["iPhone 13 Pro 128GB (UK used)"]
    assert result["created"] == ["Samsung S22 Ultra", "Old stock iPhone X"]
    assert [(e["row"], e["message"]) for e in result["errors"]] == [
        (5, "price “free” isn't a number"),
        (6, "name is missing"),
    ]
    services = {s["name"]: s for s in client.get("/api/v1/services", headers=headers).json()}
    assert services["iPhone 13 Pro 128GB (UK used)"]["description"] == "Battery 87%"
    assert services["Samsung S22 Ultra"]["price_kobo"] == 38_000_000
    assert services["Samsung S22 Ultra"]["duration_min"] == 45
    assert services["Old stock iPhone X"]["is_published"] is False

    no_price = client.post(
        "/api/v1/services/import", files={"file": ("p.csv", b"name,colour\nX,red\n", "text/csv")}, headers=headers
    )
    assert no_price.status_code == 400 and "price" in no_price.json()["detail"]
    excel = client.post(
        "/api/v1/services/import",
        files={"file": ("p.xlsx", b"PK", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        headers=headers,
    )
    assert excel.status_code == 415
    template = client.get("/api/v1/services/import/template", headers=headers)
    assert template.text.startswith("name,price,duration")


def test_service_photos_use_msflib_storage(client: TestClient, tolu: dict[str, str]) -> None:
    service = client.get("/api/v1/services", headers=tolu).json()[0]
    assert service["photo_urls"] == []
    url = f"/api/v1/services/{service['id']}/photos"
    png = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64

    uploaded = client.post(url, files={"photo": ("braids.png", png, "image/png")}, headers=tolu)
    assert uploaded.status_code == 201, uploaded.text
    photo = uploaded.json()["photo_urls"][0]
    assert photo.startswith("http://localhost/uploads/workspace/")
    assert client.get(photo.removeprefix("http://localhost")).content == png

    not_image = client.post(url, files={"photo": ("menu.pdf", b"%PDF", "application/pdf")}, headers=tolu)
    assert not_image.status_code == 415

    removed = client.delete(url, params={"url": photo}, headers=tolu)
    assert removed.json()["photo_urls"] == []
    assert client.get(photo.removeprefix("http://localhost")).status_code == 404


def test_business_settings_live_in_workspace_config(client: TestClient) -> None:
    headers = login(client, "mama@tuskapp.demo")
    updated = client.patch(
        "/api/v1/business",
        json={
            "area": "Surulere, Lagos",
            "deposit_naira": 1000,
            "hours": [{"weekday": 0, "open": "10:00", "close": "20:00"}],
        },
        headers=headers,
    ).json()
    assert updated["deposit_naira"] == 1000
    assert updated["hours"] == [{"weekday": 0, "open": "10:00", "close": "20:00"}]
    assert client.get("/api/v1/me", headers=headers).json()["business"]["deposit_naira"] == 1000

    bad = client.patch(
        "/api/v1/business", json={"hours": [{"weekday": 1, "open": "18:00", "close": "09:00"}]}, headers=headers
    )
    assert bad.status_code == 400

    about = "Smoky party jollof and soft amala for office lunches and family trays."
    profile = client.patch(
        "/api/v1/business", json={"about": about, "whatsapp": "0803 000 0002"}, headers=headers
    ).json()
    assert profile["about"] == about and profile["whatsapp"] == "0803 000 0002"
    bad_number = client.patch("/api/v1/business", json={"whatsapp": "123"}, headers=headers)
    assert bad_number.status_code == 422


def test_dashboard_requires_login(client: TestClient) -> None:
    assert client.get("/api/v1/overview").status_code == 401
