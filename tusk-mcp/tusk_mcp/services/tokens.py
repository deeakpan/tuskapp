"""Owner MCP tokens: MSFLib access tokens scoped to one business, revoked by deleting their row."""

import secrets
from dataclasses import dataclass
from datetime import timedelta

from jose import JWTError, jwt
from msflib.core.security import ALGORITHM, create_access_token
from msflib.core.store import StoreInterface
from sqlmodel import Session, select

from tusk_mcp.actions import account_action, mcp_token_action
from tusk_mcp.core.config import settings
from tusk_mcp.models import Account, AccountStatus, McpToken, McpTokenCreate, utcnow
from tusk_mcp.services.business import Business, business_by_id, business_for_account

OWNER_MCP_SCOPE = "owner_mcp"


def issue_mcp_token(
    session: Session, business: Business, account: Account, name: str, jti: str | None = None, expires: bool = True
) -> tuple[McpToken, str]:
    jti = jti or secrets.token_urlsafe(16)
    token = create_access_token(
        account.email,
        settings.SECRET_KEY,
        timedelta(days=settings.OWNER_MCP_TOKEN_DAYS) if expires else None,
        claims={"scope": OWNER_MCP_SCOPE, "workspace_id": business.id, "jti": jti},
    )
    row = mcp_token_action.create(
        session,
        data=McpTokenCreate(
            workspace_id=business.id, account_id=account.id, name=name, jti=jti, prefix=f"{token[:10]}…"
        ),
        commit=False,
    )
    return row, token


def list_mcp_tokens(session: Session, business: Business) -> list[McpToken]:
    stmt = select(McpToken).where(McpToken.workspace_id == business.id).order_by(McpToken.id.desc())
    return list(session.exec(stmt))


@dataclass
class OwnerAccess:
    account: Account
    business: Business


def verify_owner_token(session: Session, token: str, keystore: StoreInterface) -> OwnerAccess | None:
    """Owner MCP tokens must still be listed; dashboard login tokens must not be logged out."""
    try:
        claims = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None
    account = account_action.get_by_email(session, email=claims.get("sub", ""))
    if account is None or account.status not in (AccountStatus.active, AccountStatus.online):
        return None
    if claims.get("scope") == OWNER_MCP_SCOPE:
        row = mcp_token_action.get_by_all(session, jti=claims.get("jti"))
        if row is None or row.account_id != account.id or row.workspace_id != claims.get("workspace_id"):
            return None
        row.last_used_at = utcnow()
        session.add(row)
        return OwnerAccess(account, business_by_id(session, row.workspace_id))
    if keystore.check(account.email):
        return None
    business = business_for_account(session, account)
    return OwnerAccess(account, business) if business else None
