'''
Validating a token proves identity, but it does not tell you whether that identity
has permission to perform a specific action. Kubernetes provides the SubjectAccess‐
Review API for authorization checks.

SubjectAccessReview asks the Kubernetes API server: 
“Can this ServiceAccount perform this action on this resource?
'''

from kubernetes import client

authz_v1 = client.AuthorizationV1Api()


async def check_agent_permission(
    username: str,
    namespace: str,
    api_group: str,
    resource: str,
    verb: str
) -> bool:
    """Check if a ServiceAccount has permission to perform an action."""
    sar = client.V1SubjectAccessReview(
        spec=client.V1SubjectAccessReviewSpec(
            user=username, #The ServiceAccount username from TokenReview, e.g., system:service account:agents:agent-runtime.
            resource_attributes=client.V1ResourceAttributes(
                namespace=namespace,
                group=api_group, #The API group for custom resources, e.g., agents.example.com.
                resource=resource, #The resource type, e.g., customer-queries
                verb=verb, #The action being performed: get, list, create, update, delete, etc.
            )
        )
    )
    result = authz_v1.create_subject_access_review(sar) #Submit the SubjectAccessReview to the API server.
    return result.status.allowed

'''
This approach lets you leverage the Kubernetes RBAC  for
application-level permissions without building a separate authorization system.
'''