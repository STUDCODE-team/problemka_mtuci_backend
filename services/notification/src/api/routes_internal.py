"""Internal endpoints — called only by other services, not exposed to the internet."""
from fastapi import APIRouter, Depends

from api.dependencies import get_push_service, require_internal
from domain.models.schemas.email import SendOtpEmailDto
from domain.models.schemas.push import SendPushDto
from services.email_service import send_otp_email
from services.push_service import PushService

router = APIRouter(tags=["internal"], dependencies=[Depends(require_internal)])


@router.post("/push/send", status_code=204)
async def internal_send_push(
    dto: SendPushDto,
    push_service: PushService = Depends(get_push_service),
):
    await push_service.send_push_to_user(
        user_id=dto.user_id,
        title=dto.title,
        body=dto.body,
        data=dto.data,
    )


@router.post("/email/send-otp", status_code=204)
async def internal_send_otp_email(dto: SendOtpEmailDto):
    await send_otp_email(to_email=dto.to_email, otp=dto.otp)
