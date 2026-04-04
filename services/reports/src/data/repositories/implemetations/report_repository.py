from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from data.repositories.interfaces.i_report_repository import IReportRepository
from domain.models.db.report import Report
from domain.models.enums.report_category import ReportCategory
from domain.models.enums.report_status import ReportStatus


class ReportRepository(IReportRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, report: Report) -> Report:
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        return report

    async def get(self, report_id: UUID) -> Optional[Report]:
        result = await self.session.execute(
            select(Report).where(Report.id == report_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, report: Report) -> None:
        await self.session.delete(report)
        await self.session.commit()

    async def update(self, report: Report) -> Report:
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        return report

    async def get_all(
        self,
        limit: int,
        offset: int,
        status: Optional[ReportStatus] = None,
        category: Optional[ReportCategory] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[Report]:
        query = select(Report)

        if status is not None:
            query = query.where(Report.status == status)
        if category is not None:
            query = query.where(Report.category == category)
        if date_from is not None:
            query = query.where(Report.created_at >= date_from)
        if date_to is not None:
            query = query.where(Report.created_at <= date_to)

        query = query.order_by(Report.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_by_reporter(
        self,
        reporter_id: UUID,
        limit: int,
        offset: int,
        status: Optional[ReportStatus] = None,
    ) -> List[Report]:
        query = select(Report).where(Report.reporter_id == reporter_id)

        if status is not None:
            query = query.where(Report.status == status)

        query = query.order_by(Report.created_at.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())
