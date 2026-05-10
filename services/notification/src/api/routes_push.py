from fastapi import APIRouter, Depends

from api.dependencies import get_current_user, get_push_service
from common_lib.config.settings import settings
from common_lib.utils.jwt_utils import CurrentUser
from domain.models.schemas.push import PushSubscriptionDto
from services.push_service import PushService

router = APIRouter(tags=["push"])


@router.get("/vapid-public-key")
async def get_vapid_public_key():
    return {"public_key": settings.VAPID_PUBLIC_KEY}


@router.post("/subscribe", status_code=204)
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


@router.post("/unsubscribe", status_code=204)
async def push_unsubscribe(
    dto: PushSubscriptionDto,
    user: CurrentUser = Depends(get_current_user),
    push_service: PushService = Depends(get_push_service),
):
    await push_service.delete_subscription(user_id=user.id, endpoint=dto.endpoint)
