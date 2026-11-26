#When an MCP server receives a ServiceAccount token from an agent runtime when
#settling on agent identity, it must validate that token before trusting it. The same
#is true for any upstream API service that receives a request from an MCP server.
#Kubernetes provides the TokenReview API for exactly this purpose

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