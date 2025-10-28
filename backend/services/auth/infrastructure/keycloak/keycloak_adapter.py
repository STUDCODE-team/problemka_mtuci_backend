import os

from keycloak import KeycloakOpenID, KeycloakAdmin

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://keycloak:8080/")
REALM = os.getenv("REALM", "myrealm")
CLIENT_ID = os.getenv("CLIENT_ID", "auth-service-client")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", None)
KC_ADMIN = os.getenv("KEYCLOAK_ADMIN", "admin")
KC_ADMIN_PASSWORD = os.getenv("KEYCLOAK_ADMIN_PASSWORD", "admin")

keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_URL,
    client_id=CLIENT_ID,
    realm_name=REALM,
    client_secret_key=CLIENT_SECRET
)

keycloak_admin = KeycloakAdmin(
    server_url=KEYCLOAK_URL,
    username=KC_ADMIN,
    password=KC_ADMIN_PASSWORD,
    realm_name="master",
    verify=True
)


def token_for_user(username: str, password: str):
    return keycloak_openid.token(username, password)


def refresh_access_token(refresh_token: str):
    return keycloak_openid.refresh_token(refresh_token)


def logout(refresh_token: str):
    return keycloak_openid.logout(refresh_token)


def create_user(username: str, email: str, password: str):
    keycloak_admin.realm_name = REALM  # ПЕРЕДЕЛАТЬ
    user = {
        "username": username,
        "email": email,
        "enabled": True,
        "credentials": [{"type": "password", "value": password, "temporary": False}],
    }
    user_id = keycloak_admin.create_user(payload=user)
    return user_id
