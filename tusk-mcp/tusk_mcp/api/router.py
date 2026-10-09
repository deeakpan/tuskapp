from fastapi import APIRouter
from msflib.account.router import account_router, profile_router
from msflib.auth.router import router as auth_router
from msflib.notifications.router import account_notification_router

from tusk_mcp import models
from tusk_mcp.api import deps, routes
from tusk_mcp.core.config import settings

api_router = APIRouter()

api_router.include_router(
    auth_router(
        get_session=deps.get_session,
        get_keystore=deps.get_keystore,
        get_current_account=deps.get_current_account,
        account_type=models.Account,
        account_read_type=models.AccountRead,
        settings=settings,
        active_statuses=deps.ACTIVE_STATUSES,
        prefix="",
        tags=["auth"],
    )
)
api_router.include_router(
    account_router(
        get_session=deps.get_session,
        get_current_account=deps.get_current_account,
        settings=settings,
        account_type=models.Account,
        profile_type=models.Profile,
        account_read_type=models.AccountRead,
        prefix="/account",
        tags=["account"],
    )
)
api_router.include_router(
    profile_router(
        get_session=deps.get_session,
        get_current_account=deps.get_current_account,
        get_current_active_account=deps.get_current_active_account,
        settings=settings,
        profile_type=models.Profile,
        account_type=models.Account,
        profile_read_type=models.ProfileRead,
        prefix="/profiles",
        tags=["account"],
    )
)
api_router.include_router(
    account_notification_router(
        get_session=deps.get_session,
        get_current_account=deps.get_current_active_account,
        prefix="/notifications",
        tags=["notifications"],
    )
)
api_router.include_router(routes.router)
