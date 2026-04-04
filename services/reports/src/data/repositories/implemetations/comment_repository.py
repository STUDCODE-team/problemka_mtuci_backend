from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.models.db.report_comment import ReportComment


class CommentRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, comment: ReportComment) -> ReportComment:
        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)
        return comment

    async def get_by_report_id(self, report_id: UUID) -> List[ReportComment]:
        result = await self.session.execute(
            select(ReportComment)
            .where(ReportComment.report_id == report_id)
            .order_by(ReportComment.created_at.asc())
        )
        return list(result.scalars().all())
