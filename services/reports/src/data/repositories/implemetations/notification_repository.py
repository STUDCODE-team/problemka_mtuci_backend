from typing import List
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from domain.models.db.report_notification import ReportNotification


class NotificationRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, notification: ReportNotification) -> ReportNotification:
        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)
        return notification

    async def get_by_reporter(self, reporter_id: UUID) -> List[ReportNotification]:
        result = await self.session.execute(
            select(ReportNotification)
            .where(ReportNotification.reporter_id == reporter_id)
            .order_by(ReportNotification.created_at.desc())
        )
        return list(result.scalars().all())

    async def mark_read(self, notification_id: UUID, reporter_id: UUID) -> bool:
        result = await self.session.execute(
            update(ReportNotification)
            .where(
                ReportNotification.id == notification_id,
                ReportNotification.reporter_id == reporter_id,
            )
            .values(is_read=True)
        )
        await self.session.commit()
        return result.rowcount > 0

    async def mark_all_read(self, reporter_id: UUID) -> int:
        result = await self.session.execute(
            update(ReportNotification)
            .where(
                ReportNotification.reporter_id == reporter_id,
                ReportNotification.is_read == False,  # noqa: E712
            )
            .values(is_read=True)
        )
        await self.session.commit()
        return result.rowcount
