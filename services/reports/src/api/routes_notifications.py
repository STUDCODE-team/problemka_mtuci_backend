from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies import get_current_user, get_service, get_push_service
from common_lib.config.settings import settings
from common_lib.utils.jwt_utils import CurrentUser
from domain.models.schemas.notification import ReadNotificationDto
from domain.models.schemas.push_subscription import PushSubscriptionDto
from services.push_service import PushService
from services.report_service import ReportService

router = APIRouter(tags=["notifications"])


# --- In-app notifications ---

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


# --- Web Push (VAPID) ---

@router.get("/vapid-public-key")
async def get_vapid_public_key():
    return {"public_key": settings.VAPID_PUBLIC_KEY}


@router.post("/push-subscribe", status_code=204)
async def push_subscribe(
    dto: PushSubscriptionDto,
    user: CurrentUser = Depends(get_current_user),
    push_service: PushService = Depends(get_push_service),
):
    await push_service.save_subscription(
        user_id=user.id,
        endpoint=dto.endpoint,
        p256dh=dto.p256dh,
        auth=dto.auth,
    )


@router.post("/push-unsubscribe", status_code=204)
async def push_unsubscribe(
    dto: PushSubscriptionDto,
    user: CurrentUser = Depends(get_current_user),
    push_service: PushService = Depends(get_push_service),
):
    await push_service.delete_subscription(user_id=user.id, endpoint=dto.endpoint)
