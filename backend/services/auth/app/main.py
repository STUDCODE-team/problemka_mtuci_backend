import threading

from fastapi import FastAPI

from app.api.initial_setup import create_realm_and_client
from app.api.jwks_proxy import router as jwks_router
from app.api.routes_auth import router as auth_router

app = FastAPI(title="Auth Facade")
app.include_router(auth_router, prefix="/auth")
app.include_router(jwks_router)


def init():
    try:
        create_realm_and_client()
    except Exception as e:
        print("Init error:", e)


threading.Thread(target=init, daemon=True).start()
