import os, requests, time
from keycloak_facade import keycloak_admin, wait_keycloak_ready

REALM = os.getenv("REALM", "myrealm")

def create_realm_and_client():
    wait_keycloak_ready()
    realms = keycloak_admin.get_realms()
    if any(r["realm"]==REALM for r in realms):
        return
    keycloak_admin.create_realm(payload={"realm": REALM,"enabled": True})
    keycloak_admin.realm_name = REALM
    client = {"clientId":"auth-service-client","enabled":True,"publicClient":False,"directAccessGrantsEnabled":True}
    keycloak_admin.create_client(payload=client)
