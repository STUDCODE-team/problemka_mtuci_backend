import os
import time

import requests

from infrastructure.keycloak.keycloak_adapter import keycloak_admin

REALM = os.getenv("REALM", "myrealm")


def wait_keycloak_ready(timeout=60):
    start = time.time()
    url = f"{os.getenv('KEYCLOAK_URL', 'http://keycloak:8080/')}realms/master"
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


def create_realm_and_client():
    wait_keycloak_ready()

    # Проверяем, есть ли уже realm
    realms = keycloak_admin.get_realms()
    if not any(r["realm"] == REALM for r in realms):
        # Создаём realm
        keycloak_admin.create_realm(payload={"realm": REALM, "enabled": True})

    # Проверяем, есть ли уже клиент
    existing_clients = keycloak_admin.get_clients()
    if not any(c["clientId"] == "auth-service-client" for c in existing_clients):
        client = {
            "clientId": "auth-service-client",
            "enabled": True,
            "publicClient": False,
            "directAccessGrantsEnabled": True,
        }
        keycloak_admin.create_client(payload=client)
