from dataclasses import dataclass
from uuid import UUID

import jwt
from jwt.exceptions import PyJWTError

from common_lib.config.settings import settings


@dataclass
class CurrentUser:
    id: UUID
    role: str


def decode_access_token(token: str) -> CurrentUser:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except PyJWTError as exc:
        raise ValueError("Invalid token") from exc

    if payload.get("type") != "access":
        raise ValueError("Not an access token")

    return CurrentUser(
        id=UUID(payload["sub"]),
        role=payload["role"],
    )
