from datetime import datetime, timedelta, UTC
from uuid import UUID

from libs.common.config.settings import settings
from services.auth.src.data.repositories.implementations.sqlalchemy_refresh_token_repository import \
    RefreshTokenRepository
from services.auth.src.data.repositories.implementations.sqlalchemy_user_repository import UserRepository
from services.auth.src.domain.models.enums.user_roles import UserRole
from services.auth.src.services.otp_service import OTPService
from services.auth.src.services.token_service import TokenService


class AuthService:
    def __init__(
            self,
            user_repo: UserRepository,
            refresh_repo: RefreshTokenRepository,
            otp_service: OTPService,
            token_service: TokenService,
    ):
        self.user_repo = user_repo
        self.refresh_repo = refresh_repo
        self.otp_service = otp_service
        self.token_service = token_service

    async def request_otp(self, email: str) -> None:
        await self.otp_service.create_otp(email)

    async def verify_otp(self, email: str, code: str) -> dict:
        if not await self.otp_service.verify_otp(email, code):
            raise ValueError("Invalid or expired OTP")

        user = await self.user_repo.get_by_email(email)
        if not user:
            user = await self.user_repo.create(email)

        access_token = self.token_service.create_access_token(
            user_id=str(user.id),
            role=user.role.value,
        )
        refresh_token, jti = self.token_service.generate_refresh_token(str(user.id))

        expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.refresh_repo.save(
            user_id=UUID(str(user.id)),
            raw_token=refresh_token,
            jti=jti,
            expires_at=expires_at,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "role": user.role.value,
        }

    async def refresh(self, refresh_token: str) -> dict:
        payload = self.token_service.validate_refresh_token(refresh_token)
        old_jti = payload["jti"]
        user_id_str = payload["sub"]

        old_record = await self.refresh_repo.find_active_by_jti(old_jti)
        if not old_record or old_record.user_id != UUID(user_id_str):
            raise ValueError("Invalid or revoked refresh token")

        user = await self.user_repo.get_by_id(user_id_str)
        if not user:
            raise ValueError("User not found")

        new_access_token = self.token_service.create_access_token(
            user_id=str(user.id),
            role=user.role.value,
        )
        new_refresh_token, new_jti = self.token_service.generate_refresh_token(str(user.id))

        expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        await self.refresh_repo.save(
            user_id=UUID(str(user.id)),  # что за пиздец я тут сделала
            raw_token=new_refresh_token,
            jti=new_jti,
            expires_at=expires_at,
        )
        await self.refresh_repo.revoke_by_jti(old_jti)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    async def logout(self, refresh_token: str) -> None:
        try:
            payload = self.token_service.validate_refresh_token(refresh_token)
            jti = payload.get("jti")
            if jti:
                await self.refresh_repo.revoke_by_jti(jti)
        except ValueError:
            pass

    async def has_role(self, email: str, required_role: UserRole) -> bool:
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise ValueError("User not found")
        if user.role != required_role:
            raise ValueError("Insufficient permissions")
        return True
