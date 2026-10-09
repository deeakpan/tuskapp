"""Owner notifications through msflib.notifications.

Every alert lands in the dashboard. Email is for things that need the owner (a confirmed order, a
question waiting for an answer); SMS only for confirmed orders, so a phone buzz always means money in.
Chat messages and unpaid holds never leave the dashboard.
"""

from msflib.notifications.models import NotificationChannel, NotificationCreate, NotificationType
from msflib.notifications.service.notification import dispatch_account_notifications
from sqlmodel import Session

from tusk_mcp.core.config import settings
from tusk_mcp.services.business import Business, team_accounts


def sms_configured() -> bool:
    return bool(settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN and settings.TWILIO_PHONE_NUMBER)


def channels(*, email: bool = False, sms: bool = False) -> list[NotificationChannel]:
    enabled = [NotificationChannel.inapp]
    if email and settings.EMAILS_ENABLED:
        enabled.append(NotificationChannel.email)
    if sms and sms_configured():
        enabled.append(NotificationChannel.sms)
    return enabled


def notify_team(
    session: Session, business: Business, title: str, message: str, *, email: bool = False, sms: bool = False
) -> None:
    dispatch_account_notifications(
        session=session,
        settings=settings,
        data=NotificationCreate(title=title, message=message, channels=channels(email=email, sms=sms)),
        n_type=NotificationType.system,
        receivers=team_accounts(session, business),
    )


def notify_new_order(session: Session, business: Business, message: str) -> None:
    notify_team(session, business, "New booking confirmed", message, email=True, sms=True)
