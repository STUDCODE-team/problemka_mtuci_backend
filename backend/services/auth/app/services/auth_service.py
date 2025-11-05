from datetime import datetime, timedelta, UTC

import redis.asyncio as redis
from sqlalchemy.orm import Session

from app.email_sender import send_email_async
from app.services.otp_service import OTPService
from app.services.token_service import TokenService
from libs.common.config.settings import settings
from libs.common.domain.auth.i_auth_service import IAuthService
from libs.common.domain.auth.models.db.refresh_token import RefreshToken
from libs.common.domain.auth.models.db.user import User
from libs.common.domain.auth.models.enums.user_roles import UserRole
from libs.common.utils.crypto import hash_value, verify_hash


class AuthService(IAuthService):
    def __init__(self, db: Session, redis_client: redis.Redis):
        self.db = db
        self.otp_service = OTPService(redis_client)
        self.token_service = TokenService()

    async def request_otp(self, email: str):

        otp = await self.otp_service.create_otp(email)

        await send_email_async(
            to_email=email,
            subject="Ваш код подтверждения",
            body=f"Ваш одноразовый код: {otp}",
        )

        return {"detail": "OTP sent to email"}

    async def verify_otp(self, email: str, code: str):

        if not await self.otp_service.verify_otp(email, code):
            raise ValueError("Invalid or expired OTP")

        # Проверяем, есть ли пользователь
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email, role=UserRole.USER)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

        # Создаём токены
        access_token = self.token_service.create_access_token(user_id=str(user.id), role=user.role.value)
        refresh_token, jti = self.token_service.create_refresh_token(user_id=str(user.id))

        # Сохраняем refresh token
        expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
        refresh = RefreshToken(
            user_id=user.id,
            token_hash=hash_value(refresh_token),
            jti=jti,
            expires_at=expires_at,
        )
        self.db.add(refresh)
        self.db.commit()

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

        refresh_record = (
            self.db.query(RefreshToken)
            .filter(RefreshToken.jti == jti, RefreshToken.revoked_at.is_(None))
            .first()
        )

        if not refresh_record:
            raise ValueError("Refresh token not found or revoked")

        # Проверяем срок жизни
        if refresh_record.expires_at < datetime.now(UTC):
            raise ValueError("Refresh token expired")

        # Проверяем хэш
        if not verify_hash(refresh_token, refresh_record.token_hash):
            raise ValueError("Invalid refresh token")

        # Создаём новый access-токен
        user = self.db.query(User).get(user_id)
        new_access = self.token_service.create_access_token(str(user.id), user.role.value)

        return {"access_token": new_access, "refresh_token": refresh_token, "token_type": "bearer"}

    async def logout(self, refresh_token: str):
        payload = self.token_service.jwt_decode(refresh_token)
        jti = payload.get("jti")

        refresh_record = self.db.query(RefreshToken).filter(RefreshToken.jti == jti).first()
        if not refresh_record:
            return {"detail": "Already logged out"}

        refresh_record.revoked_at = datetime.now(UTC)
        self.db.commit()

        return {"detail": "Logged out successfully"}
