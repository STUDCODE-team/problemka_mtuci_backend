from datetime import datetime
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from api.dependencies import get_current_user, get_service, require_admin, require_manager
from common_lib.utils.jwt_utils import CurrentUser
from domain.models.enums.report_category import ReportCategory
from domain.models.enums.report_status import ReportStatus
from domain.models.schemas.comment import CreateCommentDto, ReadCommentDto
from domain.models.schemas.create_report import CreateReportDto
from domain.models.schemas.read_report import ReadReportDto, ReadReportListDto
from domain.models.schemas.status_history import ChangeStatusDto, ReadStatusHistoryDto
from domain.models.schemas.update_report import UpdateReportDto
from services.report_service import ReportService

router = APIRouter(tags=["reports"])


# --- My reports ---

@router.get("/my", response_model=List[ReadReportListDto])
async def get_my_reports(
    status: Optional[ReportStatus] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: CurrentUser = Depends(get_current_user),
    service: ReportService = Depends(get_service),
):
    return await service.get_my_reports(
        reporter_id=user.id,
        limit=limit,
        offset=offset,
        report_status=status,
    )


# --- CRUD ---

@router.post("/", response_model=ReadReportDto)
async def create_report(
    dto: CreateReportDto,
    user: CurrentUser = Depends(get_current_user),
    service: ReportService = Depends(get_service),
):
    return await service.create_report(dto, reporter_id=user.id)


@router.get("/", response_model=List[ReadReportListDto])
async def get_reports(
    status: Optional[ReportStatus] = None,
    category: Optional[ReportCategory] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: CurrentUser = Depends(get_current_user),
    service: ReportService = Depends(get_service),
):
    return await service.get_all_reports(
        limit=limit,
        offset=offset,
        report_status=status,
        category=category,
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/{report_id}", response_model=ReadReportDto)
async def get_report(
    report_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    service: ReportService = Depends(get_service),
):
    return await service.get_report_by_id(report_id)


@router.patch("/{report_id}", response_model=ReadReportDto)
async def update_report(
    report_id: UUID,
    dto: UpdateReportDto,
    user: CurrentUser = Depends(get_current_user),
    service: ReportService = Depends(get_service),
):
    return await service.update_report(report_id, dto)


@router.delete("/{report_id}", status_code=204)
async def delete_report(
    report_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    service: ReportService = Depends(get_service),
):
    return await service.delete_report(report_id)


# --- Status change (with FSM validation) ---

@router.patch("/{report_id}/status", response_model=ReadReportDto)
async def change_report_status(
    report_id: UUID,
    dto: ChangeStatusDto,
    user: CurrentUser = Depends(require_manager),
    service: ReportService = Depends(get_service),
):
    return await service.change_status(report_id, dto.status, changed_by=user.id)


# --- Comments ---

@router.post("/{report_id}/comments", response_model=ReadCommentDto)
async def add_comment(
    report_id: UUID,
    dto: CreateCommentDto,
    user: CurrentUser = Depends(get_current_user),
    service: ReportService = Depends(get_service),
):
    return await service.add_comment(report_id, dto, author_id=user.id)


@router.get("/{report_id}/comments", response_model=List[ReadCommentDto])
async def get_comments(
    report_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    service: ReportService = Depends(get_service),
):
    return await service.get_comments(report_id)


# --- Status History ---

@router.get("/{report_id}/history", response_model=List[ReadStatusHistoryDto])
async def get_status_history(
    report_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    service: ReportService = Depends(get_service),
):
    return await service.get_status_history(report_id)
