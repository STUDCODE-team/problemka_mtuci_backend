from fastapi import Cookie, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db import get_db
from common_lib.config.settings import settings
from common_lib.utils.jwt_utils import CurrentUser, decode_access_token
from data.repositories.push_subscription_repository import PushSubscriptionRepository
from services.push_service import PushService


async def get_current_user(
    request: Request,
    access_token: str | None = Cookie(default=None),
) -> CurrentUser:
    token = access_token
    if not token:
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        return decode_access_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def require_internal(x_internal_secret: str = Header(default="")):
    if not settings.INTERNAL_API_KEY or x_internal_secret != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


async def get_push_service(session: AsyncSession = Depends(get_db)) -> PushService:
    push_sub_repo = PushSubscriptionRepository(session)
    return PushService(push_sub_repo)
