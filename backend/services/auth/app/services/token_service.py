import uuid
from datetime import timedelta, UTC, datetime

import jwt

from libs.common.config.settings import settings


class TokenService:
    def create_access_token(self, user_id: str, role: str):
        return self.jwt_create(
            {"sub": user_id, "role": role, "type": "access"},
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

    def create_refresh_token(self, user_id: str):
        jti = str(uuid.uuid4())
        token = self.jwt_create(
            {"sub": user_id, "jti": jti, "type": "refresh"},
            timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        return token, jti

    def jwt_create(self, payload: dict, expires_delta: timedelta) -> str:
        to_encode = payload.copy()
        to_encode["exp"] = datetime.now(UTC) + expires_delta
        return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")

    def jwt_decode(self, token: str):
        return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
