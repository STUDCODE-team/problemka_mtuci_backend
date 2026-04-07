from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db import get_db
from common_lib.utils.jwt_utils import CurrentUser, decode_access_token
from data.repositories.implemetations.report_repository import ReportRepository
from data.repositories.implemetations.comment_repository import CommentRepository
from data.repositories.implemetations.status_history_repository import StatusHistoryRepository
from services.report_service import ReportService

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


def require_manager(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user.role not in ("admin", "manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or admin access required",
        )
    return user


def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


async def get_service(session: AsyncSession = Depends(get_db)):
    report_repo = ReportRepository(session)
    comment_repo = CommentRepository(session)
    history_repo = StatusHistoryRepository(session)
    return ReportService(report_repo, comment_repo, history_repo)
