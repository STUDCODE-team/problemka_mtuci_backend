from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db import get_db
from common_lib.config.settings import settings
from common_lib.utils.jwt_utils import CurrentUser, decode_access_token
from data.repositories.push_subscription_repository import PushSubscriptionRepository
from services.push_service import PushService

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> CurrentUser:
    try:
        return decode_access_token(credentials.credentials)
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
