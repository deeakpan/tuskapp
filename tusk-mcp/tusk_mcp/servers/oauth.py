"""Sign-in for the owner MCP, so owners can add it as a connector in ChatGPT or Claude.

The chat app registers itself (dynamic client registration), sends the owner to /oauth/login, and the
owner signs in with their dashboard email and password. The chat app then receives an owner MCP token,
listed in Settings like any other token and revocable there.
"""

import secrets
import time
from html import escape
from urllib.parse import urlencode

from fastapi import APIRouter, FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    AuthorizationParams,
    RefreshToken,
    TokenError,
    construct_redirect_uri,
)
from mcp.server.auth.routes import create_auth_routes, create_protected_resource_routes
from mcp.server.auth.settings import ClientRegistrationOptions, RevocationOptions
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken
from msflib.core.security import verify_password
from pydantic import AnyHttpUrl
from sqlmodel import select
from starlette.routing import Route

from tusk_mcp.actions import account_action
from tusk_mcp.api.deps import get_keystore
from tusk_mcp.core.config import settings
from tusk_mcp.db.session import session_scope
from tusk_mcp.models import AccountStatus, OAuthClient
from tusk_mcp.services.business import business_by_id, business_for_account
from tusk_mcp.services.tokens import issue_mcp_token, revoke_mcp_token, verify_owner_token

OWNER_SCOPE = "owner"
OWNER_MCP_URL = f"{settings.PUBLIC_BASE_URL}/mcp/owner/"
LOGIN_SECONDS = 15 * 60
CODE_SECONDS = 5 * 60


class OwnerCode(AuthorizationCode):
    account_id: int
    workspace_id: int


class OwnerOAuthProvider:
    """Clients live in the database (they register once); login requests and codes are minutes-long, in memory."""

    def __init__(self) -> None:
        self.logins: dict[str, tuple[float, str, AuthorizationParams]] = {}
        self.codes: dict[str, OwnerCode] = {}

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        with session_scope() as session:
            row = session.exec(select(OAuthClient).where(OAuthClient.client_id == client_id)).first()
            return OAuthClientInformationFull.model_validate(row.info) if row else None

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        with session_scope() as session:
            session.add(OAuthClient(client_id=client_info.client_id, info=client_info.model_dump(mode="json")))
            session.commit()

    async def authorize(self, client: OAuthClientInformationFull, params: AuthorizationParams) -> str:
        now = time.time()
        self.logins = {k: v for k, v in self.logins.items() if v[0] > now}
        login_id = secrets.token_urlsafe(24)
        self.logins[login_id] = (now + LOGIN_SECONDS, client.client_id, params)
        return f"{settings.PUBLIC_BASE_URL}/oauth/login?{urlencode({'id': login_id})}"

    async def load_authorization_code(self, client: OAuthClientInformationFull, authorization_code: str) -> OwnerCode | None:
        code = self.codes.get(authorization_code)
        return code if code and code.client_id == client.client_id else None

    async def exchange_authorization_code(self, client: OAuthClientInformationFull, authorization_code: OwnerCode) -> OAuthToken:
        self.codes.pop(authorization_code.code, None)
        with session_scope() as session:
            account = account_action.get(session, authorization_code.account_id)
            if account is None:
                raise TokenError("invalid_grant", "This account no longer exists.")
            business = business_by_id(session, authorization_code.workspace_id)
            _, token = issue_mcp_token(session, business, account, f"{client.client_name or 'Chat app'} (signed in)")
            session.commit()
        return OAuthToken(
            access_token=token, expires_in=settings.OWNER_MCP_TOKEN_DAYS * 24 * 3600, scope=OWNER_SCOPE
        )

    async def load_refresh_token(self, client: OAuthClientInformationFull, refresh_token: str) -> RefreshToken | None:
        return None

    async def exchange_refresh_token(
        self, client: OAuthClientInformationFull, refresh_token: RefreshToken, scopes: list[str]
    ) -> OAuthToken:
        raise TokenError("invalid_grant", "Sign in again.")

    async def load_access_token(self, token: str) -> AccessToken | None:
        with session_scope() as session:
            access = verify_owner_token(session, token, get_keystore())
            if access is None:
                return None
            return AccessToken(token=token, client_id=f"account-{access.account.id}", scopes=[OWNER_SCOPE])

    async def revoke_token(self, token: AccessToken | RefreshToken) -> None:
        with session_scope() as session:
            revoke_mcp_token(session, token.token)
            session.commit()


provider = OwnerOAuthProvider()
router = APIRouter(include_in_schema=False)


def _login_page(login_id: str, client_name: str, email: str = "", error: str = "", status_code: int = 200) -> HTMLResponse:
    alert = f"<p class=err role=alert>{escape(error)}</p>" if error else ""
    return HTMLResponse(
        "<!doctype html><html lang=en><meta charset=utf-8>"
        "<meta name=viewport content='width=device-width,initial-scale=1'><title>Sign in to TuskApp</title>"
        "<style>"
        "body{margin:0;min-height:100vh;display:grid;place-items:center;background:#0c0f0d;color:#eef2ef;"
        "font:15px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}"
        "main{width:min(380px,calc(100% - 2rem))}h1{font-size:24px;margin:0 0 .25rem;letter-spacing:-.02em}"
        "p{margin:0 0 1.5rem;color:#a7b0aa}label{display:block;font-size:13px;margin:0 0 .35rem;color:#c9d1cb}"
        "input{box-sizing:border-box;width:100%;height:44px;margin:0 0 1rem;padding:0 .85rem;border-radius:12px;"
        "border:1px solid #2a312c;background:#141916;color:inherit;font:inherit}input:focus{outline:none;border-color:#3ddc97}"
        "button{width:100%;height:46px;border:0;border-radius:12px;background:#eef2ef;color:#0c0f0d;font:600 15px system-ui;"
        "cursor:pointer}button:hover{background:#d5ddd8}.brand{color:#3ddc97;font-weight:700;letter-spacing:.08em;"
        "font-size:13px;margin-bottom:1.5rem}.err{color:#ff8a80;margin:0 0 1rem}.fine{font-size:12.5px;margin:1rem 0 0}"
        "</style><main><div class=brand>TUSKAPP</div>"
        f"<h1>Connect {escape(client_name)}</h1>"
        f"<p>Sign in with your TuskApp dashboard account to let {escape(client_name)} manage your business: "
        "bookings, customers and prices.</p>"
        f"{alert}<form method=post action='/oauth/login'><input type=hidden name=id value='{escape(login_id)}'>"
        f"<label for=email>Email</label><input id=email name=email type=email autocomplete=username required "
        f"value='{escape(email)}' autofocus>"
        "<label for=password>Password</label><input id=password name=password type=password "
        "autocomplete=current-password required><button>Sign in and connect</button></form>"
        "<p class=fine>You can disconnect any time from Settings in your dashboard.</p></main></html>",
        status_code=status_code,
    )


def _expired() -> HTMLResponse:
    return HTMLResponse(
        "<!doctype html><meta name=viewport content='width=device-width,initial-scale=1'><title>Link expired</title>"
        "<body style='margin:0;min-height:100vh;display:grid;place-items:center;background:#0c0f0d;color:#eef2ef;"
        "font:15px/1.5 system-ui,sans-serif'><main style='max-width:360px;padding:1rem'><h1>This sign-in link expired</h1>"
        "<p style='color:#a7b0aa'>Go back to ChatGPT or Claude and connect TuskApp again.</p></main>",
        status_code=400,
    )


async def _client_name(client_id: str) -> str:
    client = await provider.get_client(client_id)
    return (client.client_name if client else None) or "your chat app"


@router.get("/oauth/login", response_class=HTMLResponse)
async def login_form(id: str = "") -> HTMLResponse:
    pending = provider.logins.get(id)
    if pending is None or pending[0] < time.time():
        return _expired()
    return _login_page(id, await _client_name(pending[1]))


@router.post("/oauth/login", response_model=None)
async def login_submit(
    id: str = Form(""), email: str = Form(""), password: str = Form("")
) -> HTMLResponse | RedirectResponse:
    pending = provider.logins.get(id)
    if pending is None or pending[0] < time.time():
        return _expired()
    _, client_id, params = pending
    name = await _client_name(client_id)
    with session_scope() as session:
        account = account_action.get_by_email(session, email=email.strip().lower())
        if account is None or not verify_password(password, account.hashed_password):
            return _login_page(id, name, email, "Incorrect email or password.", 400)
        if account.status not in (AccountStatus.active, AccountStatus.online):
            return _login_page(id, name, email, "This account is not active.", 403)
        business = business_for_account(session, account)
        if business is None:
            return _login_page(id, name, email, "This account doesn't manage a business on TuskApp.", 403)
        account_id, workspace_id, subject = account.id, business.id, account.email
    provider.logins.pop(id, None)
    code = OwnerCode(
        code=secrets.token_urlsafe(32),
        scopes=params.scopes or [OWNER_SCOPE],
        expires_at=time.time() + CODE_SECONDS,
        client_id=client_id,
        code_challenge=params.code_challenge,
        redirect_uri=params.redirect_uri,
        redirect_uri_provided_explicitly=params.redirect_uri_provided_explicitly,
        resource=params.resource,
        subject=subject,
        account_id=account_id,
        workspace_id=workspace_id,
    )
    provider.codes[code.code] = code
    return RedirectResponse(
        construct_redirect_uri(str(params.redirect_uri), code=code.code, state=params.state), status_code=302
    )


def install(app: FastAPI) -> None:
    """Adds the OAuth endpoints (/authorize, /token, /register, /revoke) and their discovery documents."""
    issuer = AnyHttpUrl(settings.PUBLIC_BASE_URL)
    app.include_router(router)
    app.router.routes.extend(
        create_auth_routes(
            provider,
            issuer,
            client_registration_options=ClientRegistrationOptions(
                enabled=True, valid_scopes=[OWNER_SCOPE], default_scopes=[OWNER_SCOPE]
            ),
            revocation_options=RevocationOptions(enabled=True),
        )
    )
    resource_routes = create_protected_resource_routes(
        AnyHttpUrl(OWNER_MCP_URL), [issuer], scopes_supported=[OWNER_SCOPE], resource_name="TuskApp Owner"
    )
    app.router.routes.extend(resource_routes)
    # Some clients look the document up without the trailing slash, or at the root.
    metadata = resource_routes[0]
    for path in ("/.well-known/oauth-protected-resource/mcp/owner", "/.well-known/oauth-protected-resource"):
        app.router.routes.append(Route(path, endpoint=metadata.endpoint, methods=["GET", "OPTIONS"]))
