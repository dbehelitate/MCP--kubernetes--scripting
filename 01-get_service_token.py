'''
Kubernetes mounts the ServiceAccount token at a well-known path in every pod.
Reading it is straightforward, but you must do it correctly to avoid using expired tokens.
'''

from pathlib import Path


def get_serviceaccount_token() -> str:
    """Read the current ServiceAccount token from the filesystem."""
    token_path = Path("/var/run/secrets/kubernetes.io/serviceaccount/token")
    return token_path.read_text().strip()

'''
Read the token on every call to ensure it is current—do not cache in memory, as
Kubernetes refreshes this token automatically on the filesystem.
'''