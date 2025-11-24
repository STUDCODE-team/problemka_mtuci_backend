from fastapi import APIRouter, HTTPException, Depends

from app.services.auth_service import AuthService
from libs.common.domain.auth.models.enums.user_roles import UserRole
from libs.common.domain.auth.models.schemas.refresh_in import RefreshIn
from libs.common.domain.auth.models.schemas.request_otp import RequestOtp
from libs.common.domain.auth.models.schemas.verify_otp import VerifyOtp
from libs.common.infrastructure.db.session import get_db
from libs.common.infrastructure.redis.redis_client import get_redis

router = APIRouter()


async def get_auth_service(db=Depends(get_db), redis=Depends(get_redis)):
    return AuthService(db=db, redis_client=redis)


@router.post("/request_otp")
async def request_otp(payload: RequestOtp, service: AuthService = Depends(get_auth_service)):
    try:
        if payload.role == UserRole.ADMIN:
            return await service.has_role(payload.email, payload.role)
        return await service.request_otp(payload.email)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/verify_otp")
async def verify_otp(payload: VerifyOtp, service: AuthService = Depends(get_auth_service)):
    try:
        return await service.verify_otp(payload.email, payload.code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refresh")
async def refresh(payload: RefreshIn, service: AuthService = Depends(get_auth_service)):
    try:
        return await service.refresh(payload.refresh_token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout")
async def logout(payload: RefreshIn, service: AuthService = Depends(get_auth_service)):
    try:
        return await service.logout(payload.refresh_token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
