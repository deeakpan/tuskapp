from typing import Any

from fastapi.testclient import TestClient

HEADERS = {"Accept": "application/json, text/event-stream"}


class ToolFailed(Exception):
    pass


def call_tool(
    client: TestClient,
    server: str,
    name: str,
    arguments: dict[str, Any] | None = None,
    token: str | None = None,
    query: str = "",
    expect_status: int = 200,
) -> Any:
    headers = dict(HEADERS)
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = client.post(
        f"/mcp/{server}/{query}",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments or {}},
        },
        headers=headers,
    )
    assert response.status_code == expect_status, response.text
    if expect_status != 200:
        return None
    result = response.json()["result"]
    if result.get("isError"):
        raise ToolFailed(result["content"][0]["text"])
    structured = result["structuredContent"]
    return structured["result"] if set(structured) == {"result"} else structured
