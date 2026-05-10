import logging
from uuid import UUID

from fastapi import HTTPException, status

from common_lib.messaging import producer

logger = logging.getLogger(__name__)


async def send_otp_email(to_email: str, otp: str) -> None:
    try:
        await producer.publish_otp_email(to_email, otp)
    except Exception as e:
        logger.error("Failed to enqueue OTP email: %s", e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Message queue unavailable",
        )


async def send_push(user_id: UUID, title: str, body: str, data: dict | None = None) -> None:
    try:
        await producer.publish_push(user_id, title, body, data)
    except Exception as e:
        logger.error("Failed to enqueue push notification: %s", e)
