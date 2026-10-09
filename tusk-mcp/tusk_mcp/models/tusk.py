"""TuskApp's own tables. Businesses are MSFLib workspaces; customers are MSFLib accounts."""

from datetime import UTC, datetime
from typing import Any

from msflib.models import ModelBase, SchemaBase
from sqlalchemy import JSON, Column, DateTime, TypeDecorator, UniqueConstraint
from sqlmodel import Field, Relationship


def utcnow() -> datetime:
    return datetime.now(UTC)


class UTCDateTime(TypeDecorator):
    """Stores UTC and always returns timezone-aware datetimes (SQLite drops the offset otherwise)."""

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("Naive datetime stored; attach a timezone first.")
        return value.astimezone(UTC).replace(tzinfo=None)

    def process_result_value(self, value: datetime | None, dialect) -> datetime | None:
        return value.replace(tzinfo=UTC) if value is not None else None


class Service(ModelBase, table=True):
    __tablename__ = "tusk_service"

    workspace_id: int = Field(foreign_key="workspace.id", index=True)
    name: str
    description: str = ""
    price_kobo: int
    duration_min: int
    photo_urls: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    is_published: bool = True


class ServiceCreate(SchemaBase):
    workspace_id: int
    name: str
    description: str = ""
    price_kobo: int
    duration_min: int
    photo_urls: list[str] = Field(default_factory=list)
    is_published: bool = True


class ServiceUpdate(SchemaBase):
    name: str | None = None
    description: str | None = None
    price_kobo: int | None = None
    duration_min: int | None = None
    is_published: bool | None = None


class Customer(ModelBase, table=True):
    """A business's customer. `account_id` is their lightweight MSFLib account (used for payments)."""

    __tablename__ = "tusk_customer"
    __table_args__ = (UniqueConstraint("workspace_id", "phone_key"),)

    workspace_id: int = Field(foreign_key="workspace.id", index=True)
    account_id: int = Field(foreign_key="account.id", index=True)
    name: str
    phone: str
    phone_key: str = Field(index=True)
    email: str | None = None
    source: str = "chat"  # chat | dashboard
    conversation_id: str | None = None  # msflib conversation public_id
    first_seen_at: datetime = Field(default_factory=utcnow, sa_type=UTCDateTime)
    last_seen_at: datetime = Field(default_factory=utcnow, sa_type=UTCDateTime)

    bookings: list["Booking"] = Relationship(back_populates="customer")


class CustomerCreate(SchemaBase):
    workspace_id: int
    account_id: int
    name: str
    phone: str
    phone_key: str
    email: str | None = None
    source: str = "chat"


class CustomerUpdate(SchemaBase):
    name: str | None = None
    phone: str | None = None
    phone_key: str | None = None
    email: str | None = None
    conversation_id: str | None = None
    last_seen_at: datetime | None = None


class Booking(ModelBase, table=True):
    __tablename__ = "tusk_booking"

    ref: str = Field(unique=True, index=True)
    workspace_id: int = Field(foreign_key="workspace.id", index=True)
    service_id: int = Field(foreign_key="tusk_service.id")
    customer_id: int = Field(foreign_key="tusk_customer.id", index=True)
    service_name: str
    start: datetime = Field(sa_type=UTCDateTime, index=True)
    end: datetime = Field(sa_type=UTCDateTime)
    notes: str = ""
    total_kobo: int
    deposit_kobo: int
    status: str = "held"  # held | confirmed | cancelled | expired
    hold_expires_at: datetime | None = Field(default=None, sa_type=UTCDateTime)
    payment_id: int | None = Field(default=None, foreign_key="payment.id")
    booked_at: datetime = Field(default_factory=utcnow, sa_type=UTCDateTime)

    customer: Customer = Relationship(back_populates="bookings")


class BookingCreate(SchemaBase):
    ref: str
    workspace_id: int
    service_id: int
    customer_id: int
    service_name: str
    start: datetime
    end: datetime
    notes: str = ""
    total_kobo: int
    deposit_kobo: int
    status: str = "held"
    hold_expires_at: datetime | None = None


class BookingUpdate(SchemaBase):
    status: str | None = None
    payment_id: int | None = None


class BlockedSlot(ModelBase, table=True):
    __tablename__ = "tusk_blocked_slot"

    workspace_id: int = Field(foreign_key="workspace.id", index=True)
    start: datetime = Field(sa_type=UTCDateTime)
    end: datetime = Field(sa_type=UTCDateTime)
    reason: str = ""


class BlockedSlotCreate(SchemaBase):
    workspace_id: int
    start: datetime
    end: datetime
    reason: str = ""


class Enquiry(ModelBase, table=True):
    """A customer question the business's data couldn't answer, waiting for the owner."""

    __tablename__ = "tusk_enquiry"

    workspace_id: int = Field(foreign_key="workspace.id", index=True)
    customer_id: int | None = Field(default=None, foreign_key="tusk_customer.id")
    question: str
    answer: str = ""
    status: str = "open"  # open | answered
    asked_at: datetime = Field(default_factory=utcnow, sa_type=UTCDateTime)

    customer: Customer | None = Relationship()


class EnquiryCreate(SchemaBase):
    workspace_id: int
    customer_id: int | None = None
    question: str


class EnquiryUpdate(SchemaBase):
    answer: str | None = None
    status: str | None = None


class McpCallLog(ModelBase, table=True):
    __tablename__ = "tusk_mcp_call_log"

    workspace_id: int | None = Field(default=None, foreign_key="workspace.id", index=True)
    server: str  # customer | owner
    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    status: str
    duration_ms: int
    called_at: datetime = Field(default_factory=utcnow, sa_type=UTCDateTime, index=True)


class McpCallLogCreate(SchemaBase):
    workspace_id: int | None = None
    server: str
    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    status: str
    duration_ms: int


class McpToken(ModelBase, table=True):
    """An owner MCP token: an MSFLib access token whose `jti` must still be listed here to be valid."""

    __tablename__ = "tusk_mcp_token"

    workspace_id: int = Field(foreign_key="workspace.id", index=True)
    account_id: int = Field(foreign_key="account.id")
    name: str
    jti: str = Field(unique=True, index=True)
    prefix: str
    last_used_at: datetime | None = Field(default=None, sa_type=UTCDateTime)
    issued_at: datetime = Field(default_factory=utcnow, sa_type=UTCDateTime)


class McpTokenCreate(SchemaBase):
    workspace_id: int
    account_id: int
    name: str
    jti: str
    prefix: str


class OAuthClient(ModelBase, table=True):
    """A chat app (Claude, ChatGPT...) that registered itself to sign owners in to the owner MCP."""

    __tablename__ = "tusk_oauth_client"

    client_id: str = Field(unique=True, index=True)
    info: dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))


class McpTokenUpdate(SchemaBase):
    last_used_at: datetime | None = None


class Empty(SchemaBase):
    pass
