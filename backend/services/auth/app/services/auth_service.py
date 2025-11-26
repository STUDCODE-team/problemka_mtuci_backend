from datetime import datetime, timedelta, timezone

import redis.asyncio as redis
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from libs.common.config.settings import settings
from libs.common.domain.auth.i_auth_service import IAuthService
from libs.common.domain.auth.models.db.refresh_token import RefreshToken
from libs.common.domain.auth.models.db.user import User
from libs.common.domain.auth.models.enums.user_roles import UserRole
from libs.common.utils.crypto import hash_value, verify_hash
from services.auth.app.services.otp_service import OTPService
from services.auth.app.services.token_service import TokenService


class AuthService(IAuthService):
    def __init__(self, db: AsyncSession, redis_client: redis.Redis):
        print("AuthService init called")
        self.db = db
        self.otp_service = OTPService(redis_client)
        self.token_service = TokenService()

    async def request_otp(self, email: str):
        otp = await self.otp_service.create_otp(email)
        # await send_email_async(to_email=email, subject="Ваш код подтверждения", body=f"Ваш одноразовый код: {otp}")
        return {"otp": otp}

    async def verify_otp(self, email: str, code: str):
        if not await self.otp_service.verify_otp(email, code):
            raise ValueError("Invalid or expired OTP")

        # Проверяем, есть ли пользователь
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            user = User(email=email, role=UserRole.USER)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)

        # Создаём токены
        access_token = self.token_service.create_access_token(user_id=str(user.id), role=user.role.value)
        refresh_token, jti = self.token_service.create_refresh_token(user_id=str(user.id))

        # Сохраняем refresh token
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh = RefreshToken(
            user_id=user.id,
            token_hash=hash_value(refresh_token),
            jti=jti,
            expires_at=expires_at,
        )
        self.db.add(refresh)
        await self.db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "role": user.role.value,
        }

    async def refresh(self, refresh_token: str):
        payload = self.token_service.jwt_decode(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")

        jti = payload.get("jti")
        user_id = payload.get("sub")

        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.jti == jti, RefreshToken.revoked_at.is_(None))
        )
        refresh_record = result.scalar_one_or_none()
        if not refresh_record:
            raise ValueError("Refresh token not found or revoked")

        if refresh_record.expires_at < datetime.now(timezone.utc):
            raise ValueError("Refresh token expired")

        if not verify_hash(refresh_token, refresh_record.token_hash):
            raise ValueError("Invalid refresh token")

        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("User not found")

        new_access = self.token_service.create_access_token(str(user.id), user.role.value)

        return {"access_token": new_access, "refresh_token": refresh_token, "token_type": "bearer"}

    async def logout(self, refresh_token: str):
        payload = self.token_service.jwt_decode(refresh_token)
        jti = payload.get("jti")

        result = await self.db.execute(select(RefreshToken).where(RefreshToken.jti == jti))
        refresh_record = result.scalar_one_or_none()
        if not refresh_record:
            return {"detail": "Already logged out"}

        refresh_record.revoked_at = datetime.now(timezone.utc)
        await self.db.commit()

        return {"detail": "Logged out successfully"}

    async def has_role(self, email: str, role: UserRole):
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.role != role:
            raise HTTPException(status_code=403, detail="Access denied")

        return True
