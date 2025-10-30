from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()


class LoginIn(BaseModel):
    username: str
    password: str


class RegisterIn(BaseModel):
    username: str
    email: str
    password: str


class RefreshIn(BaseModel):
    refresh_token: str


@router.post("/request_otp")
def login(payload: LoginIn):
    try:
        return auth_service.login(payload.username, payload.password)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/verify_otp")
def register(payload: RegisterIn):
    try:
        return auth_service.register(payload.username, payload.email, payload.password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refresh")
def refresh(payload: RefreshIn):
    try:
        return auth_service.refresh(payload.refresh_token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout")
def logout(payload: RefreshIn):
    try:
        return auth_service.logout(payload.refresh_token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
