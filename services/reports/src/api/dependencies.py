from fastapi import Cookie, Depends, Header, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db import get_db
from common_lib.config.settings import settings
from common_lib.utils.jwt_utils import CurrentUser, decode_access_token
from data.repositories.implemetations.report_repository import ReportRepository
from data.repositories.implemetations.comment_repository import CommentRepository
from data.repositories.implemetations.status_history_repository import StatusHistoryRepository
from data.repositories.implemetations.notification_repository import NotificationRepository
from services.report_service import ReportService


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


async def get_service(session: AsyncSession = Depends(get_db)) -> ReportService:
    report_repo = ReportRepository(session)
    comment_repo = CommentRepository(session)
    history_repo = StatusHistoryRepository(session)
    notification_repo = NotificationRepository(session)
    return ReportService(report_repo, comment_repo, history_repo, notification_repo)
