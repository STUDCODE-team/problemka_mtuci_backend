from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from libs.common.infrastructure.db.session import get_db
from libs.common.infrastructure.redis.redis_client import get_redis
from services.auth.src.data.repositories.implementations.sqlalchemy_refresh_token_repository import \
    RefreshTokenRepository
from services.auth.src.data.repositories.implementations.sqlalchemy_user_repository import UserRepository
from services.auth.src.services.auth_service import AuthService
from services.auth.src.services.jwt_provider import PyJWTTokenProvider
from services.auth.src.services.otp_service import OTPService
from services.auth.src.services.token_service import TokenService


# Вспомогательные зависимости
async def get_user_repository(session: AsyncSession = Depends(get_db)):
    return UserRepository(session)


async def get_refresh_token_repository(session: AsyncSession = Depends(get_db)):
    return RefreshTokenRepository(session)


async def get_otp_service(redis_client=Depends(get_redis)):
    return OTPService(redis_client)


async def get_token_service():
    return TokenService(token_provider=PyJWTTokenProvider())


# Главная зависимость
async def get_auth_service(
        user_repo=Depends(get_user_repository),
        refresh_repo=Depends(get_refresh_token_repository),
        otp_service=Depends(get_otp_service),
        token_service=Depends(get_token_service),
):
    return AuthService(
        user_repo=user_repo,
        refresh_repo=refresh_repo,
        otp_service=otp_service,
        token_service=token_service,
    )
