from msflib.account.actions import AccountAction, ProfileAction
from msflib.actions import ModelAction
from msflib.notifications.actions import AccountNotificationAction, NotificationAction
from msflib.tenancy import TenantAction
from msflib.workspace_config.actions import ScopedConfigAction
from msflib.workspace_config.service import ScopedConfigService
from msflib.workspaces.actions import UserAction, WorkspaceAction

from tusk_mcp.core.config import settings
from tusk_mcp.models import (
    Account,
    AccountCreate,
    AccountUpdate,
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
    Profile,
    ProfileCreate,
    ProfileUpdate,
    Service,
    ServiceCreate,
    ServiceUpdate,
    Tenant,
    TenantCreate,
    TenantUpdate,
    User,
    UserCreate,
    UserUpdate,
    Workspace,
    WorkspaceCreate,
    WorkspaceUpdate,
)

tenant_action = TenantAction[Tenant, TenantCreate, TenantUpdate]()
profile_action = ProfileAction[Profile, ProfileCreate, ProfileUpdate]()
account_action = AccountAction[Account, AccountCreate, AccountUpdate](
    settings=settings, profile_action=profile_action
)
workspace_action = WorkspaceAction[Workspace, WorkspaceCreate, WorkspaceUpdate](settings=settings)
user_action = UserAction[User, UserCreate, UserUpdate]()

config_service = ScopedConfigService(ScopedConfigAction())
notification_action = NotificationAction()
account_notification_action = AccountNotificationAction()

service_action = ModelAction[Service, ServiceCreate, ServiceUpdate]()
customer_action = ModelAction[Customer, CustomerCreate, CustomerUpdate]()
booking_action = ModelAction[Booking, BookingCreate, BookingUpdate]()
blocked_slot_action = ModelAction[BlockedSlot, BlockedSlotCreate, Empty]()
enquiry_action = ModelAction[Enquiry, EnquiryCreate, EnquiryUpdate]()
call_log_action = ModelAction[McpCallLog, McpCallLogCreate, Empty]()
mcp_token_action = ModelAction[McpToken, McpTokenCreate, McpTokenUpdate]()
