from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.models.db.report_status_history import ReportStatusHistory


class StatusHistoryRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, entry: ReportStatusHistory) -> ReportStatusHistory:
        self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)
        return entry

    async def get_by_report_id(self, report_id: UUID) -> List[ReportStatusHistory]:
        result = await self.session.execute(
            select(ReportStatusHistory)
            .where(ReportStatusHistory.report_id == report_id)
            .order_by(ReportStatusHistory.changed_at.asc())
        )
        return list(result.scalars().all())
