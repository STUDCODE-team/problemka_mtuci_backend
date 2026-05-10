from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import get_current_user, get_service
from common_lib.utils.jwt_utils import CurrentUser
from domain.models.schemas.notification import ReadNotificationDto
from services.report_service import ReportService

router = APIRouter(tags=["notifications"])


@router.get("/my", response_model=List[ReadNotificationDto])
async def get_my_notifications(
    user: CurrentUser = Depends(get_current_user),
    service: ReportService = Depends(get_service),
):
    return await service.get_my_notifications(reporter_id=user.id)


@router.patch("/{notification_id}/read", status_code=204)
async def mark_notification_read(
    notification_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    service: ReportService = Depends(get_service),
):
    found = await service.mark_notification_read(notification_id, reporter_id=user.id)
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")


@router.post("/read-all", status_code=204)
async def mark_all_notifications_read(
    user: CurrentUser = Depends(get_current_user),
    service: ReportService = Depends(get_service),
):
    await service.mark_all_notifications_read(reporter_id=user.id)
