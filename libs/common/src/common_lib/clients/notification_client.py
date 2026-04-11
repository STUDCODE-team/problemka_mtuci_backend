import logging
from uuid import UUID

import httpx
from fastapi import HTTPException, status

from common_lib.config.settings import settings
from common_lib.utils.trace import current_trace_id

logger = logging.getLogger(__name__)

_BASE = f"{settings.NOTIFICATION_SERVICE_URL}/internal"


def _headers() -> dict:
    headers = {"X-Internal-Secret": settings.INTERNAL_API_KEY}
    trace_id = current_trace_id()
    if trace_id:
        headers["X-Trace-Id"] = trace_id
    return headers


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
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(f"{_BASE}/email/send-otp", json=payload, headers=_headers())
            resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        try:
            detail = e.response.json()
        except Exception:
            detail = e.response.text
        raise HTTPException(status_code=e.response.status_code, detail=detail)
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Notification service is unreachable",
        )
