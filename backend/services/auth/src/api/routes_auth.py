# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException

from services.auth.src.api.dependencies import get_auth_service
from services.auth.src.domain.models.enums.user_roles import UserRole
from services.auth.src.domain.models.schemas.refresh_in import RefreshIn
from services.auth.src.domain.models.schemas.request_otp import RequestOtp
from services.auth.src.domain.models.schemas.verify_otp import VerifyOtp
from services.auth.src.services.auth_service import AuthService

router = APIRouter()


@router.post("/request_otp")
async def request_otp(
        payload: RequestOtp,
        service: AuthService = Depends(get_auth_service),
):
    try:
        if payload.role == UserRole.ADMIN:
            await service.has_role(payload.email, payload.role)
        return await service.request_otp(payload.email)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/verify_otp")
async def verify_otp(
        payload: VerifyOtp,
        service: AuthService = Depends(get_auth_service),
):
    return await service.verify_otp(payload.email, payload.code)


@router.post("/refresh")
async def refresh(
        payload: RefreshIn,
        service: AuthService = Depends(get_auth_service),
):
    return await service.refresh(payload.refresh_token)


@router.post("/logout")
async def logout(
        payload: RefreshIn,
        service: AuthService = Depends(get_auth_service),
):
    await service.logout(payload.refresh_token)
    return {"detail": "Logged out successfully"}
