from typing import List
from uuid import UUID

from services.reports.src.data.repositories.implemetations.report_repository import ReportRepository
from services.reports.src.domain.i_report_service import IReportService
from services.reports.src.domain.models.db.report import Report
from services.reports.src.domain.models.enums.report_status import ReportStatus
from services.reports.src.domain.models.schemas.create_report import CreateReportDto
from services.reports.src.domain.models.schemas.read_report import ReadReportDto
from services.reports.src.domain.models.schemas.update_report import UpdateReportDto


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
        report = await self.repo.get(report_id)
        if not report:
            raise ValueError(f"Report with id {report_id} not found")
        return report

    async def delete_report(
            self,
            report_id: UUID
    ) -> None:
        report = await self.repo.get(report_id)
        if not report:
            raise ValueError(f"Report with id {report_id} not found")
        await self.repo.delete(report)

    async def update_report(
            self,
            report_id: UUID,
            data: UpdateReportDto
    ) -> ReadReportDto:
        report = await self.repo.get(report_id)
        if not report:
            raise ValueError(f"Report with id {report_id} not found")

        if data.type is not None:
            report.type = data.type
        if data.status is not None:
            report.status = data.status
        if data.isExplicit is not None:
            report.is_explicit = data.isExplicit

        updated_report = await self.repo.update(report)
        return ReadReportDto.model_validate(updated_report)

    async def get_all_reports(
            self,
            limit: int = 50,
            offset: int = 0
    ) -> List[ReadReportDto]:
        reports = await self.repo.get_all(limit=limit, offset=offset)
        return [ReadReportDto.model_validate(report) for report in reports]
