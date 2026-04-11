import logging
from uuid import UUID

import httpx

from common_lib.config.settings import settings

logger = logging.getLogger(__name__)

_BASE = f"{settings.NOTIFICATION_SERVICE_URL}/internal"


def _headers() -> dict:
    return {"X-Internal-Secret": settings.INTERNAL_API_KEY}


async def send_push(user_id: UUID, title: str, body: str, data: dict | None = None) -> None:
    payload = {
        "user_id": str(user_id),
        "title": title,
        "body": body,
        "data": data,
    }
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(f"{_BASE}/push/send", json=payload, headers=_headers())
            resp.raise_for_status()
    except Exception as e:
        logger.error("Failed to send push notification: %s", e)


async def send_otp_email(to_email: str, otp: str) -> None:
    payload = {"to_email": to_email, "otp": otp}
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(f"{_BASE}/email/send-otp", json=payload, headers=_headers())
        resp.raise_for_status()
