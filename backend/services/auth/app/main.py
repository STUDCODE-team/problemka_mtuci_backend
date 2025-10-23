from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from keycloak_facade import token_for_user, create_user, refresh_token, logout
from jwks_proxy import router as jwks_router
from initial_setup import create_realm_and_client
import threading

app = FastAPI(title="Auth Facade")
app.include_router(jwks_router)

def init():
    try:
        create_realm_and_client()
    except Exception as e:
        print("Init error:", e)

threading.Thread(target=init, daemon=True).start()

class LoginIn(BaseModel):
    username: str
    password: str

class RegisterIn(BaseModel):
    username: str
    email: str
    password: str

@app.post("/login")
def login(payload: LoginIn):
    try:
        return token_for_user(payload.username, payload.password)
    except Exception as e:
        raise HTTPException(401, str(e))

@app.post("/register")
def register(payload: RegisterIn):
    try:
        return {"id": create_user(payload.username, payload.email, payload.password)}
    except Exception as e:
        raise HTTPException(400, str(e))

@app.post("/refresh")
def refresh(payload: dict):
    if "refresh_token" not in payload:
        raise HTTPException(400,"missing refresh_token")
    return refresh_token(payload["refresh_token"])

@app.post("/logout")
def do_logout(payload: dict):
    if "refresh_token" not in payload:
        raise HTTPException(400,"missing refresh_token")
    return logout(payload["refresh_token"])
