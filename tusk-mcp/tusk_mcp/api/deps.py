from typing import Annotated

from fastapi import Depends, HTTPException, status
from msflib.api.deps import get_keystore_factory, get_session_factory
from msflib.auth.deps import get_account_dependencies
from sqlmodel import Session

from tusk_mcp.core.config import settings
from tusk_mcp.db.session import engine
from tusk_mcp.models import Account, AccountStatus
from tusk_mcp.services.business import Business, business_for_account

ACTIVE_STATUSES = [AccountStatus.active, AccountStatus.online]

get_session = get_session_factory(engine)

# Redis when configured, otherwise an in-process MapStore (logouts reset on restart).
get_keystore = get_keystore_factory(
    redis_host=settings.REDIS_HOST,
    redis_password=settings.REDIS_PASSWORD,
    redis_port=int(settings.REDIS_PORT) if settings.REDIS_PORT else 6379,
)

account_dependencies = get_account_dependencies(
    AccountModel=Account,
    oauth_token_url=f"{settings.API_V1_STR}/login",
    secret_key=settings.SECRET_KEY,
    active_statuses=ACTIVE_STATUSES,
    session_dep=get_session,
    keystore_dep=get_keystore,
)

get_current_account = account_dependencies.get_current_account
get_current_active_account = account_dependencies.get_current_active_account


def get_current_business(
    session: Annotated[Session, Depends(get_session)],
    account: Annotated[Account, Depends(get_current_active_account)],
) -> Business:
    business = business_for_account(session, account)
    if business is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No business set up for this account.")
    return business


SessionDep = Annotated[Session, Depends(get_session)]
CurrentAccount = Annotated[Account, Depends(get_current_active_account)]
CurrentBusiness = Annotated[Business, Depends(get_current_business)]
