from typing import List
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from domain.models.db.push_subscription import PushSubscription


class PushSubscriptionRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert(self, user_id: UUID, endpoint: str, p256dh: str, auth: str) -> PushSubscription:
        # Replace existing subscription with same endpoint
        await self.session.execute(
            delete(PushSubscription).where(PushSubscription.endpoint == endpoint)
        )
        sub = PushSubscription(user_id=user_id, endpoint=endpoint, p256dh=p256dh, auth=auth)
        self.session.add(sub)
        await self.session.commit()
        await self.session.refresh(sub)
        return sub

    async def get_by_user(self, user_id: UUID) -> List[PushSubscription]:
        result = await self.session.execute(
            select(PushSubscription).where(PushSubscription.user_id == user_id)
        )
        return list(result.scalars().all())

    async def delete_by_endpoint(self, endpoint: str, user_id: UUID) -> None:
        await self.session.execute(
            delete(PushSubscription).where(
                PushSubscription.endpoint == endpoint,
                PushSubscription.user_id == user_id,
            )
        )
        await self.session.commit()

    async def delete_by_user(self, user_id: UUID) -> None:
        await self.session.execute(
            delete(PushSubscription).where(PushSubscription.user_id == user_id)
        )
        await self.session.commit()
