import os
from keycloak import KeycloakOpenID, KeycloakAdmin
import httpx
import time

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://keycloak:8080/")
REALM = os.getenv("REALM", "myrealm")
KC_ADMIN = os.getenv("KEYCLOAK_ADMIN", "admin")
KC_ADMIN_PASSWORD = os.getenv("KEYCLOAK_ADMIN_PASSWORD", "admin")

# OpenID client used for token endpoints (client must be created during initial_setup)
# We'll set client_id to "auth-service-client" in initial setup
CLIENT_ID = os.getenv("CLIENT_ID", "auth-service-client")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", None)  # initial_setup will fill if needed

keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_URL,
    client_id=CLIENT_ID,
    realm_name=REALM,
    client_secret_key=CLIENT_SECRET
)

# Admin client for management (realm, users)
keycloak_admin = KeycloakAdmin(server_url=KEYCLOAK_URL, username=KC_ADMIN, password=KC_ADMIN_PASSWORD, realm_name="master", verify=True)

# JWKS proxy: fetch Keycloak JWKS URI
async def fetch_jwks():
    # calls keycloak realm certs endpoint and returns JSON
    jwks_url = f"{KEYCLOAK_URL}realms/{REALM}/protocol/openid-connect/certs"
    async with httpx.AsyncClient() as c:
        r = await c.get(jwks_url, timeout=10.0)
        r.raise_for_status()
        return r.json()

def token_for_user(username: str, password: str):
    return keycloak_openid.token(username, password)

def refresh_token(refresh_token: str):
    return keycloak_openid.refresh_token(refresh_token)

def logout(refresh_token: str):
    return keycloak_openid.logout(refresh_token)

def create_user(username: str, email: str, password: str):
    # uses admin client to create user and set password
    user = {
        "username": username,
        "email": email,
        "enabled": True,
        "credentials": [{"type": "password", "value": password, "temporary": False}],
    }
    user_id = keycloak_admin.create_user(payload=user)
    return user_id

# small helper to wait until keycloak ready
def wait_keycloak_ready(timeout=60):
    start = time.time()
    url = f"{KEYCLOAK_URL}realms/master"
    import requests
    while True:
        try:
            r = requests.get(url, timeout=3)
            if r.status_code in (200, 302, 401):
                return True
        except Exception:
            pass
        if time.time() - start > timeout:
            raise TimeoutError("Keycloak did not become ready in time")
        time.sleep(1)


