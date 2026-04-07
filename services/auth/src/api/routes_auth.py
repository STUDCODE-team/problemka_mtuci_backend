# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from api.dependencies import get_auth_service
from common_lib.utils.jwt_utils import CurrentUser, decode_access_token
from domain.models.enums.user_roles import UserRole
from domain.models.schemas.refresh_in import RefreshIn
from domain.models.schemas.request_otp import RequestOtp
from domain.models.schemas.user_info import UserInfoDto
from domain.models.schemas.verify_otp import VerifyOtp
from services.auth_service import AuthService

router = APIRouter()
bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentUser:
    try:
        return decode_access_token(credentials.credentials)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


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
    try:
        return await service.verify_otp(payload.email, payload.code)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


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


@router.get("/me", response_model=UserInfoDto)
async def get_me(
    user: CurrentUser = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    user_info = await service.get_user_by_id(user.id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
    return UserInfoDto.model_validate(user_info)
