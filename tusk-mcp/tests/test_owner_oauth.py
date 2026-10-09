"""Adding the owner MCP as a connector: ChatGPT/Claude register, the owner signs in, the connector gets a token."""

import base64
import hashlib
import secrets
from urllib.parse import parse_qs, urlsplit

from fastapi.testclient import TestClient

from tests.mcp_client import call_tool

REDIRECT = "https://claude.ai/api/mcp/auth_callback"


def test_owner_connects_by_signing_in(client: TestClient, tolu: dict[str, str]) -> None:
    challenge = client.post("/mcp/owner/", json={}, headers={"Accept": "application/json, text/event-stream"})
    assert challenge.status_code == 401
    assert "/.well-known/oauth-protected-resource/mcp/owner/" in challenge.headers["www-authenticate"]

    resource = client.get("/.well-known/oauth-protected-resource/mcp/owner/").json()
    assert resource["resource"] == "http://localhost/mcp/owner/"
    server = client.get("/.well-known/oauth-authorization-server").json()
    assert server["registration_endpoint"] == "http://localhost/register"

    registered = client.post(
        "/register",
        json={
            "redirect_uris": [REDIRECT],
            "client_name": "Claude",
            "token_endpoint_auth_method": "none",
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code"],
        },
    )
    assert registered.status_code == 201, registered.text
    client_id = registered.json()["client_id"]

    verifier = secrets.token_urlsafe(48)
    code_challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    authorize = client.get(
        "/authorize",
        params={
            "response_type": "code",
            "client_id": client_id,
            "redirect_uri": REDIRECT,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "state": "abc",
            "scope": "owner",
            "resource": resource["resource"],
        },
        follow_redirects=False,
    )
    assert authorize.status_code == 302, authorize.text
    login_url = urlsplit(authorize.headers["location"])
    login_id = parse_qs(login_url.query)["id"][0]

    page = client.get(f"/oauth/login?id={login_id}")
    assert "Connect Claude" in page.text

    wrong = client.post("/oauth/login", data={"id": login_id, "email": "tolu@tuskapp.demo", "password": "nope"})
    assert wrong.status_code == 400 and "Incorrect email or password" in wrong.text

    signed_in = client.post(
        "/oauth/login",
        data={"id": login_id, "email": "tolu@tuskapp.demo", "password": "tusk-demo-123"},
        follow_redirects=False,
    )
    assert signed_in.status_code == 302
    back = urlsplit(signed_in.headers["location"])
    assert f"{back.scheme}://{back.netloc}{back.path}" == REDIRECT
    query = parse_qs(back.query)
    assert query["state"] == ["abc"]

    token = client.post(
        "/token",
        data={
            "grant_type": "authorization_code",
            "code": query["code"][0],
            "redirect_uri": REDIRECT,
            "client_id": client_id,
            "code_verifier": verifier,
        },
    )
    assert token.status_code == 200, token.text
    access_token = token.json()["access_token"]

    assert isinstance(call_tool(client, "owner", "list_bookings", token=access_token), list)
    tokens = client.get("/api/v1/mcp-tokens", headers=tolu).json()
    connected = next(t for t in tokens if t["name"] == "Claude (signed in)")

    reused = client.post(
        "/token",
        data={"grant_type": "authorization_code", "code": query["code"][0], "redirect_uri": REDIRECT,
              "client_id": client_id, "code_verifier": verifier},
    )
    assert reused.status_code == 400

    client.delete(f"/api/v1/mcp-tokens/{connected['id']}", headers=tolu)
    call_tool(client, "owner", "list_bookings", token=access_token, expect_status=401)
