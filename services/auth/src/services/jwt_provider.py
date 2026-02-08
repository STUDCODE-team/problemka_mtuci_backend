from datetime import datetime
from uuid import UUID

import jwt
from jwt.exceptions import PyJWTError

from common_lib.config.settings import settings
from data.repositories.interfaces.i_token_repository import TokenProvider


class PyJWTTokenProvider(TokenProvider):
    ALGORITHM = "HS256"

    def create_access_token(self, user_id: str, role: str, expires_at: datetime) -> str:
        payload = {
            "sub": user_id,
            "role": role,
            "type": "access",
            "exp": expires_at,
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=self.ALGORITHM)

    def create_refresh_token(self, jti: UUID, user_id: str, expires_at: datetime) -> str:
        payload = {
            "sub": user_id,
            "jti": str(jti),
            "type": "refresh",
            "exp": expires_at,
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=self.ALGORITHM)

    def decode_and_verify(self, token: str) -> dict:
        try:
            return jwt.decode(token, settings.JWT_SECRET, algorithms=[self.ALGORITHM])
        except PyJWTError as exc:
            raise ValueError("Invalid token") from exc

    def decode_access_token(self, token: str) -> dict:
        payload = self.decode_and_verify(token)
        if payload.get("type") != "access":
            raise ValueError("Not an access token")
        return payload

    def decode_refresh_token(self, token: str) -> dict:
        payload = self.decode_and_verify(token)
        if payload.get("type") != "refresh":
            raise ValueError("Not a refresh token")
        return payload
