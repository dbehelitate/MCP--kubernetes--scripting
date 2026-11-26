#In server identity, the MCP server uses its own ServiceAccount token when calling
#upstream APIs. For agent identity, the agent sends in its ServiceAccount token, and
#after validation the MCP copies this agent token over into the Authorization: HTTP
#header when it makes its request to any upstream API.

import httpx
from pathlib import Path


async def call_upstream_with_service_token(
    endpoint: str,
    payload: dict,
    user_id: str | None = None
) -> dict:
    """Call upstream API with the MCP server's ServiceAccount token."""
    sa_token = get_serviceaccount_token()
    headers = {
        "Authorization": f"Bearer {sa_token}",
        "Content-Type": "application/json"
    }
    if user_id:
        payload["_audit_user_id"] = user_id

    async with httpx.AsyncClient() as client:
        response = await client.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()