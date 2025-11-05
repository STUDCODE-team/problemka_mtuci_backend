from fastapi import APIRouter, HTTPException

from app.services.auth_service import AuthService
from libs.common.domain.auth.models.schemas.request_otp import RequestOtp
from libs.common.domain.auth.models.schemas.verify_otp import VerifyOtp
from libs.common.infrastructure.redis.redis_client import init_redis

router = APIRouter()
auth_service = AuthService()


@app.on_event("startup")
async def startup_event():
    await init_redis("redis://localhost:6379/0")  # или другой URL твоего Redis


@router.post("/request_otp")
def request_otp(payload: RequestOtp):
    try:
        return auth_service.request_otp(payload.email)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/verify_otp")
def verify_otp(payload: VerifyOtp):
    try:
        return auth_service.register(payload.email, payload.code)
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
