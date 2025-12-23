from datetime import datetime, timedelta, UTC
from uuid import uuid4

from libs.common.config.settings import settings
from services.auth.src.data.repositories.interfaces.i_token_repository import TokenProvider


class TokenService:
    def __init__(self, token_provider: TokenProvider):
        self.provider = token_provider

    def create_access_token(self, user_id: str, role: str) -> str:
        expires_at = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        return self.provider.create_access_token(user_id, role, expires_at)

    def generate_refresh_token(self, user_id: str) -> tuple[str, str]:
        jti = uuid4()
        expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        token = self.provider.create_refresh_token(jti, user_id, expires_at)
        return token, str(jti)  # jti возвращаем только для сохранения в БД

    def validate_access_token(self, token: str) -> dict:
        return self.provider.decode_access_token(token)

    def validate_refresh_token(self, token: str) -> dict:
        return self.provider.decode_refresh_token(token)
