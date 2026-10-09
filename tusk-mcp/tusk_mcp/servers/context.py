"""Shared plumbing for the MCP servers: owner auth, the business a call is about, and call logging."""

import functools
import inspect
import json
import os
import time
from collections.abc import Callable
from contextvars import ContextVar
from typing import Any
from urllib.parse import urlsplit

from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.provider import AccessToken
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError
from mcp.server.lowlevel.server import request_ctx
from mcp.server.transport_security import TransportSecuritySettings

from tusk_mcp.api.deps import get_keystore
from tusk_mcp.core.config import settings
from tusk_mcp.db.session import session_scope
from tusk_mcp.services.business import BookingError, NotFound, log_call
from tusk_mcp.services.tokens import verify_owner_token

_workspace_id: ContextVar[int | None] = ContextVar("tusk_workspace_id", default=None)


def use_workspace(workspace_id: int) -> None:
    """Records which business the current tool call is about, for the call log."""
    _workspace_id.set(workspace_id)


def link_business() -> str | None:
    """Business slug from a shareable link such as `/mcp/customer?b=glam-by-tolu`."""
    try:
        request = request_ctx.get().request
    except LookupError:
        return None
    return request.query_params.get("b") if request is not None else None


class OwnerToken(AccessToken):
    account_id: int
    workspace_id: int


class OwnerTokenVerifier:
    """Accepts owner MCP tokens made on the dashboard, and dashboard login tokens."""

    async def verify_token(self, token: str) -> AccessToken | None:
        with session_scope() as session:
            access = verify_owner_token(session, token, get_keystore())
            if access is None:
                return None
            return OwnerToken(
                token=token,
                client_id=f"account-{access.account.id}",
                scopes=["owner"],
                account_id=access.account.id,
                workspace_id=access.business.id,
            )


def transport_security() -> TransportSecuritySettings:
    public = urlsplit(settings.PUBLIC_BASE_URL)
    local = ["127.0.0.1", "localhost", "[::1]"]
    public_hosts = {public.netloc}
    if railway_domain := os.environ.get("RAILWAY_PUBLIC_DOMAIN"):
        public_hosts.add(railway_domain)
    hosts = [*public_hosts, *(f"{host}:*" for host in local), *local]
    origins = [*(f"https://{host}" for host in public_hosts), f"{public.scheme}://{public.netloc}"]
    origins += [f"http://{host}:*" for host in local]
    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True, allowed_hosts=hosts, allowed_origins=origins
    )


def owner_workspace() -> int:
    token = get_access_token()
    if not isinstance(token, OwnerToken):
        raise ToolError("Not signed in. Connect with an owner token from the TuskApp dashboard.")
    return token.workspace_id


def _loggable(arguments: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(arguments, default=str))


def logged_tool(mcp: FastMCP, server: str, **tool_options: Any) -> Callable:
    """`mcp.tool` that logs every call per business and turns business errors into tool errors."""

    def decorator(fn: Callable) -> Callable:
        def finish(arguments: dict[str, Any], started: float, status: str) -> None:
            with session_scope() as session:
                log_call(
                    session,
                    server=server,
                    tool=fn.__name__,
                    workspace_id=_workspace_id.get(),
                    arguments=_loggable(arguments),
                    status=status,
                    duration_ms=int((time.perf_counter() - started) * 1000),
                )

        if inspect.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def wrapper(**arguments: Any) -> Any:
                started, status, reset = time.perf_counter(), "error", _workspace_id.set(None)
                try:
                    result = await fn(**arguments)
                    status = "ok"
                    return result
                except (NotFound, BookingError) as exc:
                    raise ToolError(str(exc)) from exc
                finally:
                    finish(arguments, started, status)
                    _workspace_id.reset(reset)

        else:

            @functools.wraps(fn)
            def wrapper(**arguments: Any) -> Any:
                started, status, reset = time.perf_counter(), "error", _workspace_id.set(None)
                try:
                    result = fn(**arguments)
                    status = "ok"
                    return result
                except (NotFound, BookingError) as exc:
                    raise ToolError(str(exc)) from exc
                finally:
                    finish(arguments, started, status)
                    _workspace_id.reset(reset)

        mcp.tool(**tool_options)(wrapper)
        return fn

    return decorator
