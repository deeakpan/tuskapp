"""Customer chats stored as msflib.conversation DMs between the customer's account and the assistant."""

from typing import Any

from msflib.conversation.actions import ConversationAction, MessageAction
from msflib.conversation.contracts import ConversationScope, Participant
from msflib.conversation.integrations.ai_bridge import ConversationTranscriptWriter
from msflib.conversation.models.enums import MemberKind, MessageType, SenderKind
from msflib.conversation.services import ChannelService
from sqlmodel import Session

from tusk_mcp.db.session import engine, session_scope
from tusk_mcp.models import Customer
from tusk_mcp.services.business import Business, business_by_id

AGENT_ID = "tuskapp-assistant"

channel_service = ChannelService()
conversation_action = ConversationAction()
message_action = MessageAction()


def _customer_participant(business: Business, customer: Customer) -> Participant:
    return Participant(
        kind=MemberKind.user, id=str(customer.account_id), tenant_id=business.workspace.tenant_id
    )


def _scope(business: Business, conversation_id: str | None = None) -> ConversationScope:
    return ConversationScope(
        tenant_id=business.workspace.tenant_id, workspace_id=business.id, conversation_id=conversation_id
    )


def ensure_conversation(session: Session, business: Business, customer: Customer) -> str:
    """The customer's conversation with the business, created on first contact. Commits the session."""
    if customer.conversation_id:
        return customer.conversation_id
    agent = Participant(kind=MemberKind.agent, id=AGENT_ID, tenant_id=business.workspace.tenant_id)
    conversation, _ = channel_service.create_direct(
        session, scope=_scope(business), participants=[_customer_participant(business, customer), agent]
    )
    customer.conversation_id = conversation.public_id
    session.add(customer)
    session.commit()
    return conversation.public_id


def record_chat(workspace_id: int, customer_id: int, turns: list[tuple[str, str]]) -> None:
    """Appends ("customer" | "assistant", text) turns to the customer's conversation.

    Call after the tool's own session has committed: the transcript writer opens its own sessions.
    """
    with session_scope() as session:
        business = business_by_id(session, workspace_id)
        customer = session.get(Customer, customer_id)
        conversation_id = ensure_conversation(session, business, customer)
        user = _customer_participant(business, customer)
        scope = _scope(business, conversation_id)
    writer = ConversationTranscriptWriter(lambda: Session(engine), scope=scope, user=user, agent_id=AGENT_ID)
    for speaker, text in turns:
        if speaker == "customer":
            writer.write_user_turn(text)
        else:
            writer.write_agent_turn(text)


def transcript(session: Session, business: Business, customer: Customer, limit: int = 200) -> list[dict[str, Any]]:
    if not customer.conversation_id:
        return []
    conversation = conversation_action.get_by_all(session, public_id=customer.conversation_id)
    if conversation is None or conversation.workspace_id != business.id:
        return []
    messages = message_action.list_for_conversation(session, conversation_id=conversation.id, limit=limit)
    return [
        {
            "id": m.id,
            "from": "customer" if m.sender_kind == SenderKind.user else "assistant",
            "text": m.content,
            "at": m.created_at,
        }
        for m in reversed(messages)
        if m.deleted_at is None and m.message_type == MessageType.message
    ]
