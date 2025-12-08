from typing import List
from uuid import UUID

from services.reports.app.data.repositories.report_repository import ReportRepository
from services.reports.app.domain.i_report_service import IReportService
from services.reports.app.domain.models.db.report import Report
from services.reports.app.domain.models.enums.report_status import ReportStatus
from services.reports.app.domain.models.schemas.create_report import CreateReportDto
from services.reports.app.domain.models.schemas.read_report import ReadReportDto
from services.reports.app.domain.models.schemas.update_report import UpdateReportDto


class ReportService(IReportService):

    def __init__(self, repo: ReportRepository):
        self.repo = repo

    async def create_report(self, report_id: UUID, dto: CreateReportDto, reporter_id: UUID) -> ReadReportDto:
        report = Report(
            id=report_id,
            type=dto.type,
            is_explicit=dto.is_explicit,
            reporter_id=reporter_id,
            status=ReportStatus.DRAFT,
        )

        report = await self.repo.create(report)
        return ReadReportDto.model_validate(report)

    async def get_report_by_id(
            self,
            report_id: UUID
    ) -> ReadReportDto:
        pass

    async def delete_report(
            self,
            report_id: UUID
    ) -> None:
        pass

    async def update_report(
            self,
            report_id: UUID,
            data: UpdateReportDto
    ) -> ReadReportDto:
        pass

    async def get_all_reports(
            self,
            limit: int = 50,
            offset: int = 0
    ) -> List[ReadReportDto]:
        pass
