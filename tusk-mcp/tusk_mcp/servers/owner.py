from datetime import date
from typing import Annotated, Any

from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field
from sqlmodel import Session

from tusk_mcp import views
from tusk_mcp.core.config import settings
from tusk_mcp.db.session import session_scope
from tusk_mcp.servers.context import (
    OwnerTokenVerifier,
    logged_tool,
    owner_workspace,
    transport_security,
    use_workspace,
)
from tusk_mcp.services import business as biz
from tusk_mcp.services.business import Business

READ_ONLY = ToolAnnotations(readOnlyHint=True)

mcp = FastMCP(
    "TuskApp Owner",
    instructions=(
        "Tools for a business owner or staff member to manage their own business on TuskApp: "
        "bookings, customers, prices, blocked dates and customer insights."
    ),
    stateless_http=True,
    json_response=True,
    streamable_http_path="/",
    transport_security=transport_security(),
    token_verifier=OwnerTokenVerifier(),
    auth=AuthSettings(
        issuer_url=settings.PUBLIC_BASE_URL,
        resource_server_url=f"{settings.PUBLIC_BASE_URL}/mcp/owner/",
        required_scopes=["owner"],
        validate_token_resource=False,
    ),
)


def tool(**options: Any):
    return logged_tool(mcp, "owner", **options)


def current_business(session: Session) -> Business:
    workspace_id = owner_workspace()
    use_workspace(workspace_id)
    return biz.business_by_id(session, workspace_id)


@tool(annotations=READ_ONLY)
def list_bookings(
    date: Annotated[date | None, Field(description="Only this day, YYYY-MM-DD. Omit for all.")] = None,
) -> list[dict[str, Any]]:
    """Bookings for my business, earliest first."""
    with session_scope() as session:
        return [views.booking_detail(b) for b in biz.list_bookings(session, current_business(session), date)]


@tool(annotations=READ_ONLY)
def list_customers(
    query: Annotated[str | None, Field(description="Name, phone or email to search for")] = None,
) -> list[dict[str, Any]]:
    """Customers who booked or asked questions, with their phone and email."""
    with session_scope() as session:
        return [views.customer_detail(c) for c in biz.list_customers(session, current_business(session), query)]


@tool()
def update_service(
    service_id: Annotated[int, Field(description="Service id")],
    price_naira: Annotated[int | None, Field(description="New price in Naira", gt=0)] = None,
    duration: Annotated[str | None, Field(description="New duration, e.g. '90 mins', '3 days', '1 week'")] = None,
    is_published: Annotated[bool | None, Field(description="Show or hide from customers")] = None,
) -> dict[str, Any]:
    """Change a service's price, duration or visibility."""
    duration_min = biz.parse_duration(duration) if duration else None
    with session_scope() as session:
        service = biz.update_service(
            session,
            current_business(session),
            service_id,
            price_kobo=price_naira * 100 if price_naira is not None else None,
            duration_min=duration_min,
            is_published=is_published,
        )
        return views.service_card(service)


@tool()
def block_dates(
    start_date: Annotated[date, Field(description="First day to block, YYYY-MM-DD")],
    end_date: Annotated[date | None, Field(description="Last day to block. Defaults to start_date.")] = None,
    reason: str = "",
) -> dict[str, Any]:
    """Stop customers booking on these days. Existing bookings are not cancelled."""
    with session_scope() as session:
        clashes = biz.block_dates(session, current_business(session), start_date, end_date or start_date, reason)
        return {
            "blocked": f"{start_date:%a %d %b}" + (f" to {end_date:%a %d %b}" if end_date else ""),
            "existing_bookings_on_those_days": [views.booking_detail(b) for b in clashes],
        }


@tool(annotations=READ_ONLY)
def get_insights() -> dict[str, Any]:
    """What customers asked about, popular services and days, bookings and unanswered questions."""
    with session_scope() as session:
        return biz.insights(session, current_business(session))


@tool()
def cancel_booking(ref: Annotated[str, Field(description="Booking ref, e.g. GBT-0412")]) -> dict[str, Any]:
    """Cancel one of my bookings."""
    with session_scope() as session:
        return views.booking_detail(biz.cancel_booking(session, current_business(session), ref))
