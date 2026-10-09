import os
from urllib.parse import urlsplit

from msflib.account.config import AccountSettings
from msflib.auth.config import AuthSettings
from msflib.conversation.config import ConversationSettings
from msflib.core.config import CoreSettings, SettingsBase
from msflib.notifications.config import NotificationSettings
from msflib.payments.config import PaymentsSettings
from msflib.tenancy import TenancySettings
from msflib.workspaces.config import WorkspaceSettings


class AppSettings(
    PaymentsSettings,
    NotificationSettings,
    ConversationSettings,
    WorkspaceSettings,
    TenancySettings,
    AccountSettings,
    AuthSettings,
    CoreSettings,
    SettingsBase,
):
    PROJECT_NAME: str = "TuskApp"
    # Fixed dev key so dashboard sessions survive restarts; set SECRET_KEY in .env for anything shared.
    SECRET_KEY: str = "dev-only-change-me-in-env-file-0123456789"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    USE_SQLITE: bool = True
    SQLITE_DATABASE_URI: str = "sqlite:///./tusk.db"

    # Each business gets its own workspace at signup; customers never get one.
    AUTO_REGISTER_EVENT_HOOKS: bool = False
    AUTO_CREATE_DEFAULT_WORKSPACE: bool = False

    # Owner notifications also go out by email once SMTP_* is configured and this is true.
    EMAILS_ENABLED: bool | None = False

    REDIS_HOST: str | None = None
    REDIS_PORT: str | None = None
    REDIS_PASSWORD: str | None = None

    # SMS notifications (msflib.notifications reads these).
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_PHONE_NUMBER: str = ""

    HOST: str = "127.0.0.1"
    PORT: int = 8100
    # Public HTTPS URL (ngrok / Cloudflare Tunnel) when connecting ChatGPT; used for MCP and payment links.
    PUBLIC_BASE_URL: str = "http://127.0.0.1:8100"
    # Public website (the dashboard app); each business's profile lives at SITE_URL/<slug>.
    SITE_URL: str = "http://localhost:3000"
    # Turns business addresses and customers' "near ..." into coordinates. Empty disables distance ranking.
    GEOCODER_URL: str = "https://nominatim.openstreetmap.org/search"
    GEOCODER_USER_AGENT: str = "TuskApp/0.1 (hello@tuskapp.app)"
    # Bucket (s3, gcs) or container (azure) for uploads; MSFLib's file and cloudinary storage don't use it.
    STORAGE_BUCKET: str = ""
    HOLD_MINUTES: int = 30
    # Deposit every new business starts with (owners can change it, or set 0, in Settings).
    DEFAULT_DEPOSIT_NAIRA: int = 2_000
    OWNER_MCP_TOKEN_DAYS: int = 365
    # Creates the Glam by Tolu / Mama Put Kitchen demo accounts on an empty database.
    SEED_DEMO: bool = True


settings = AppSettings()

# Railway sets RAILWAY_PUBLIC_DOMAIN. Use it while PUBLIC_BASE_URL is unset or still a placeholder;
# an explicit URL (e.g. a custom domain) wins.
if (railway_domain := os.environ.get("RAILWAY_PUBLIC_DOMAIN")) and urlsplit(settings.PUBLIC_BASE_URL).hostname in (
    "127.0.0.1",
    "localhost",
    "your-railway-url.up.railway.app",
):
    settings.PUBLIC_BASE_URL = f"https://{railway_domain}"
