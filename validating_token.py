#When an MCP server receives a ServiceAccount token from an agent runtime when
#settling on agent identity, it must validate that token before trusting it. The same
#is true for any upstream API service that receives a request from an MCP server.
#Kubernetes provides the TokenReview API for exactly this purpose

#The TokenReview API takes a token as input and returns whether it is valid, along
#with the identity it represents. 
#This script shows an example of how an MCP server
#can interact with the Kubernetes API to validate the token.

import httpx
from kubernetes import client, config

config.load_incluster_config()
auth_v1 = client.AuthenticationV1Api()


async def validate_agent_runtime_token(token: str) -> dict:
    """Validate agent runtime token using Kubernetes TokenReview API."""
    token_review = client.V1TokenReview(
        spec=client.V1TokenReviewSpec(token=token)
    )
    result = auth_v1.create_token_review(token_review)

    if not result.status.authenticated:
        raise ValueError("Token validation failed: not authenticated")

    username = result.status.user.username
    if not username.startswith("system:serviceaccount:agents:"):
        raise ValueError(f"Token from unauthorized namespace: {username}")

    return {
        "username": username,
        "uid": result.status.user.uid,
        "groups": result.status.user.groups