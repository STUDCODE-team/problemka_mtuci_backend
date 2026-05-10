import asyncio
import json
import logging
from uuid import UUID

from pywebpush import webpush, WebPushException

from common_lib.config.settings import settings
from data.repositories.implemetations.push_subscription_repository import PushSubscriptionRepository

logger = logging.getLogger(__name__)


class PushService:

    def __init__(self, push_sub_repo: PushSubscriptionRepository):
        self.push_sub_repo = push_sub_repo

    async def save_subscription(
        self, user_id: UUID, endpoint: str, p256dh: str, auth: str
    ) -> None:
        await self.push_sub_repo.upsert(user_id, endpoint, p256dh, auth)

    async def delete_subscription(self, user_id: UUID, endpoint: str) -> None:
        await self.push_sub_repo.delete_by_endpoint(endpoint, user_id)

    async def send_push_to_user(self, user_id: UUID, title: str, body: str, data: dict | None = None) -> None:
        if not settings.VAPID_PRIVATE_KEY or not settings.VAPID_PUBLIC_KEY:
            logger.warning("VAPID keys not configured, skipping Web Push")
            return

        subscriptions = await self.push_sub_repo.get_by_user(user_id)
        if not subscriptions:
            return

        payload = json.dumps({"title": title, "body": body, **(data or {})})
        vapid_claims = {"sub": f"mailto:{settings.VAPID_CONTACT_EMAIL}"}

        stale_endpoints = []
        for sub in subscriptions:
            try:
                await asyncio.to_thread(
                    webpush,
                    subscription_info={
                        "endpoint": sub.endpoint,
                        "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
                    },
                    data=payload,
                    vapid_private_key=settings.VAPID_PRIVATE_KEY,
                    vapid_claims=vapid_claims,
                )
            except WebPushException as e:
                if e.response is not None and e.response.status_code in (404, 410):
                    # Subscription expired or unregistered
                    stale_endpoints.append(sub.endpoint)
                else:
                    logger.error("WebPush error for endpoint %s: %s", sub.endpoint, e)

        for endpoint in stale_endpoints:
            await self.push_sub_repo.delete_by_endpoint(endpoint, user_id)
