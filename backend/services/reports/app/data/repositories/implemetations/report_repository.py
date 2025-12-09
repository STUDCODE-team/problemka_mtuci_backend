from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.reports.app.data.repositories.interfaces.i_report_repository import IReportRepository
from services.reports.app.domain.models.db.report import Report


class ReportRepository(IReportRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, report: Report):
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        return report

    async def get(self, report_id: UUID):
        result = await self.session.execute(
            select(Report).where(Report.id == report_id)
        )
        return result.scalar_one_or_none()

    async def delete(self, report: Report):
        await self.session.delete(report)
        await self.session.commit()

    async def update(self, report: Report):
        self.session.add(report)
        await self.session.commit()
        await self.session.refresh(report)
        return report

    async def get_all(self, limit: int, offset: int):
        result = await self.session.execute(
            select(Report)
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
