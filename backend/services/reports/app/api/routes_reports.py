from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from services.reports.app.data.repositories.implemetations.report_repository import ReportRepository
from services.reports.app.domain.models.schemas.create_report import CreateReportDto
from services.reports.app.domain.models.schemas.update_report import UpdateReportDto
from services.reports.app.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


def get_service(session: AsyncSession = Depends()):
    repo = ReportRepository(session)
    return ReportService(repo)


@router.post("/")
async def create_report(
        dto: CreateReportDto,
        reporter_id: UUID,
        service: ReportService = Depends(get_service)
):
    return await service.create_report(reporter_id, dto)


@router.get("/{report_id}")
async def get_report(
        report_id: UUID,
        service: ReportService = Depends(get_service)
):
    return await service.get_report_by_id(report_id)


@router.get("/")
async def get_reports(
        limit: int = 50,
        offset: int = 0,
        service: ReportService = Depends(get_service)
):
    return await service.get_all_reports(limit, offset)


@router.patch("/{report_id}")
async def update_report(
        report_id: UUID,
        dto: UpdateReportDto,
        service: ReportService = Depends(get_service)
):
    return await service.update_report(report_id, dto)


@router.delete("/{report_id}")
async def delete_report(
        report_id: UUID,
        service: ReportService = Depends(get_service)
):
    return await service.delete_report(report_id)
