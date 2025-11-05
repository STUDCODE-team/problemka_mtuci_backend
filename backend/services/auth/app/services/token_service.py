import uuid
from datetime import timedelta, UTC, datetime

import jwt

from libs.common.config.settings import settings


class TokenService:
    def create_access_token(self, user_id: str, role: str):
        return self.jwt_create(
            {"sub": user_id, "role": role, "type": "access"},
            timedelta(minutes=settings.access_token_expire_minutes)
        )

    def create_refresh_token(self, user_id: str):
        jti = str(uuid.uuid4())
        token = self.jwt_create(
            {"sub": user_id, "jti": jti, "type": "refresh"},
            timedelta(days=settings.refresh_token_expire_days)
        )
        return token, jti

    def jwt_create(self, payload: dict, expires_delta: timedelta) -> str:
        to_encode = payload.copy()
        to_encode["exp"] = datetime.now(UTC) + expires_delta
        return jwt.encode(to_encode, settings.jwt_secret, algorithm="HS256")

    def jwt_decode(self, token: str):
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
