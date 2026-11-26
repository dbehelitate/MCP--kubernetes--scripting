'''
This script shows an example of how an MCP server can interact with the Kubernetes API to validate the token.

When an MCP server receives a ServiceAccount token from an agent runtime when it must validate the token.
The same is true for any upstream API service that receives a request from an MCP server.

Kubernetes provides the TokenReview API for exactly this purpose:
TokenReview API takes a token as input and returns whether it is valid, along with the identity it represents. 
'''

import httpx
from kubernetes import client, config

config.load_incluster_config()
auth_v1 = client.AuthenticationV1Api()
#Load the Kubernetes configuration from the in-cluster service account.


async def validate_agent_runtime_token(token: str) -> dict:
    """Validate agent runtime token using Kubernetes TokenReview API."""
    token_review = client.V1TokenReview(
        spec=client.V1TokenReviewSpec(token=token) 
        #Create a TokenReview object with the token to validate.
    )
    result = auth_v1.create_token_review(token_review) 
    #Submit the TokenReview to the Kubernetes API server. This is a synchronous call

    if not result.status.authenticated: 
        raise ValueError("Token validation failed: not authenticated")

    username = result.status.user.username  
    #Extract the ServiceAccount username in the format system:serviceaccount:namespace:name.


    if not username.startswith("system:serviceaccount:agents:"): 
        #Enforce an allowlist policy: accept tokens only from the agents namespace.
        raise ValueError(f"Token from unauthorized namespace: {username}")

    return {
        "username": username,
        "uid": result.status.user.uid,
        "groups": result.status.user.groups

'''
This validation step is critical for security.
By calling TokenReview, the MCP server confirms that the Kubernetes API server issued and signed this token.

The allowlist check is a simple namespace-based filter for initial access control:
- It restricts which ServiceAccounts can use this MCP server.
- It prevents pods from unrelated namespaces from calling your tools. 

For fine-grained authorization based on RBAC policies, use SubjectAccessReview, as described in the next script.

Token validation adds some small latency. 
You can cache validation results keyed by the token’s hash with a short time-to-live (TTL) 
but ensure that the cache respects token expiration.
'''
