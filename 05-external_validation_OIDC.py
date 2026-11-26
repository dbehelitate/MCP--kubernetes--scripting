'''
To validate ServiceAccount tokens OUTSIDE the cluster:

Kubernetes can expose ServiceAccount tokens as OIDC-compliant JWTs
that any OIDC-aware service can validate. 

Most managed Kubernetes services enable by default an OIDC issuer URL
'''

import jwt
import httpx


async def validate_sa_token_externally(
    token: str,
    cluster_issuer: str,
    expected_audience: str
) -> dict:
    """Validate a Kubernetes ServiceAccount token using OIDC discovery."""
    discovery_url = f"{cluster_issuer}/.well-known/openid-configuration"

    async with httpx.AsyncClient() as client:
        discovery_resp = await client.get(discovery_url)
        discovery_resp.raise_for_status()
        discovery = discovery_resp.json()

        jwks_uri = discovery["jwks_uri"] 
        #Retrieve the JSON Web Key Set containing the public keys used to sign tokens.
        jwks_resp = await client.get(jwks_uri)
        jwks_resp.raise_for_status()
        jwks = jwks_resp.json()

    signing_key = jwt.PyJWKClient(jwks_uri).get_signing_key_from_jwt(token)
    #Extract the correct signing key based on the token’s key ID header.

    claims = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        audience=expected_audience,
        #Validate the token’s audience claim to ensure it is intended for your service.
        issuer=cluster_issuer
    )
    return claims
    #Return the validated claims, including the ServiceAccount identity.
