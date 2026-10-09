"""Every table the app uses. Table creation discovers tables through this import."""

from msflib.account.models import (
    AccountCreate,
    AccountRead,
    AccountRole,
    AccountStatus,
    AccountUpdate,
    ProfileCreate,
    ProfileRead,
    ProfileUpdate,
)
from msflib.account.models.account import Account, Profile
from msflib.conversation.models import Conversation, ConversationMember, ConversationThread, Message
from msflib.notifications.models import AccountNotification, Notification
from msflib.payments.models import Payment, PaymentQueue
from msflib.tenancy.models import TenantCreate, TenantUpdate
from msflib.tenancy.models.tenant import Tenant
from msflib.workspace_config.models import ScopedConfigEntry
from msflib.workspaces.models import (
    UserCreate,
    UserType,
    UserUpdate,
    WorkspaceCreate,
    WorkspaceStatus,
    WorkspaceUpdate,
)
from msflib.workspaces.models.user import User
from msflib.workspaces.models.workspace import Workspace

from .tusk import (
    BlockedSlot,
    BlockedSlotCreate,
    Booking,
    BookingCreate,
    BookingUpdate,
    Customer,
    CustomerCreate,
    CustomerUpdate,
    Empty,
    Enquiry,
    EnquiryCreate,
    EnquiryUpdate,
    McpCallLog,
    McpCallLogCreate,
    McpToken,
    McpTokenCreate,
    McpTokenUpdate,
    Service,
    ServiceCreate,
    ServiceUpdate,
    UTCDateTime,
    utcnow,
)
