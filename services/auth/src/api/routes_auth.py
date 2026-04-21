from uuid import UUID

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from pydantic import BaseModel

from api.dependencies import get_auth_service
from common_lib.config.settings import settings
from common_lib.utils.jwt_utils import CurrentUser, decode_access_token
from domain.models.enums.user_roles import UserRole
from domain.models.schemas.request_otp import RequestOtp
from domain.models.schemas.user_info import UserInfoDto
from domain.models.schemas.verify_otp import VerifyOtp
from services.auth_service import AuthService

router = APIRouter()

_ACCESS_MAX_AGE = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
_REFRESH_MAX_AGE = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="strict",
        max_age=_ACCESS_MAX_AGE,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="strict",
        max_age=_REFRESH_MAX_AGE,
        path=settings.COOKIE_REFRESH_PATH,
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path=settings.COOKIE_REFRESH_PATH)


async def get_current_user(
    access_token: str | None = Cookie(default=None),
) -> CurrentUser:
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        return decode_access_token(access_token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user


@router.post("/request_otp")
async def request_otp(
    payload: RequestOtp,
    service: AuthService = Depends(get_auth_service),
):
    try:
        if payload.role.is_privileged:
            await service.has_privileged_role(payload.email)
        return await service.request_otp(payload.email)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/verify_otp")
async def verify_otp(
    response: Response,
    payload: VerifyOtp,
    service: AuthService = Depends(get_auth_service),
):
    try:
        tokens = await service.verify_otp(payload.email, payload.code)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    _set_auth_cookies(response, tokens["access_token"], tokens["refresh_token"])
    return {"token_type": "bearer", "role": tokens["role"]}


@router.post("/refresh")
async def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    service: AuthService = Depends(get_auth_service),
):
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        tokens = await service.refresh(refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    _set_auth_cookies(response, tokens["access_token"], tokens["refresh_token"])
    return {"token_type": "bearer"}


@router.post("/logout")
async def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    service: AuthService = Depends(get_auth_service),
):
    if refresh_token:
        await service.logout(refresh_token)
    _clear_auth_cookies(response)
    return {"detail": "Logged out successfully"}


@router.get("/me", response_model=UserInfoDto)
async def get_me(
    user: CurrentUser = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    user_info = await service.get_user_by_id(user.id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
    return UserInfoDto(
        id=user_info.id,
        email=user_info.email,
        role=user_info.role,
        is_active=user_info.is_active,
        created_at=user_info.created_at,
    )


@router.get("/users", response_model=list[UserInfoDto])
async def list_users(
    _: CurrentUser = Depends(require_admin),
    service: AuthService = Depends(get_auth_service),
):
    return await service.get_all_users()


class SetRoleBody(BaseModel):
    role: UserRole


@router.get("/users/{user_id}", response_model=UserInfoDto)
async def get_user_by_id(
    user_id: UUID,
    _: CurrentUser = Depends(require_admin),
    service: AuthService = Depends(get_auth_service),
):
    user_info = await service.get_user_by_id(user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
    return UserInfoDto(
        id=user_info.id,
        email=user_info.email,
        role=user_info.role,
        is_active=user_info.is_active,
        created_at=user_info.created_at,
    )


@router.patch("/users/{user_id}/role", response_model=UserInfoDto)
async def set_user_role(
    user_id: UUID,
    body: SetRoleBody,
    _: CurrentUser = Depends(require_admin),
    service: AuthService = Depends(get_auth_service),
):
    return await service.set_user_role(user_id, body.role)
