import os

import httpx

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://keycloak:8080/")
REALM = os.getenv("REALM", "myrealm")


async def fetch_jwks():
    jwks_url = f"{KEYCLOAK_URL}realms/{REALM}/protocol/openid-connect/certs"
    async with httpx.AsyncClient() as client:
        r = await client.get(jwks_url, timeout=10.0)
        r.raise_for_status()
        return r.json()
