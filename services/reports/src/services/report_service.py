from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import HTTPException, status

from common_lib.clients import notification_client
from data.repositories.implemetations.report_repository import ReportRepository
from data.repositories.implemetations.comment_repository import CommentRepository
from data.repositories.implemetations.status_history_repository import StatusHistoryRepository
from data.repositories.implemetations.notification_repository import NotificationRepository
from domain.models.db.report import Report
from domain.models.db.report_comment import ReportComment
from domain.models.db.report_notification import ReportNotification
from domain.models.db.report_status_history import ReportStatusHistory
from domain.models.enums.report_category import ReportCategory
from domain.models.enums.report_status import ReportStatus, ALLOWED_STATUS_TRANSITIONS
from domain.models.schemas.create_report import CreateReportDto
from domain.models.schemas.notification import ReadNotificationDto
from domain.models.schemas.read_report import ReadReportDto, ReadReportListDto
from domain.models.schemas.update_report import UpdateReportDto
from domain.models.schemas.comment import ReadCommentDto, CreateCommentDto
from domain.models.schemas.status_history import ReadStatusHistoryDto


class ReportService:

    def __init__(
        self,
        report_repo: ReportRepository,
        comment_repo: CommentRepository,
        history_repo: StatusHistoryRepository,
        notification_repo: NotificationRepository,
    ):
        self.report_repo = report_repo
        self.comment_repo = comment_repo
        self.history_repo = history_repo
        self.notification_repo = notification_repo

    async def create_report(self, dto: CreateReportDto, reporter_id: UUID) -> ReadReportDto:
        report = Report(
            id=uuid4(),
            title=dto.title,
            description=dto.description,
            location=dto.location,
            room=dto.room,
            category=dto.category,
            priority=dto.priority,
            type=dto.type,
            photo_url=dto.photo_url,
            reporter_id=reporter_id,
            status=ReportStatus.NEW,
        )
        report = await self.report_repo.create(report)
        return ReadReportDto.model_validate(report)

    async def get_report_by_id(self, report_id: UUID) -> ReadReportDto:
        report = await self._get_report_or_404(report_id)
        return ReadReportDto.model_validate(report)

    async def delete_report(self, report_id: UUID) -> None:
        report = await self._get_report_or_404(report_id)
        await self.report_repo.delete(report)

    async def update_report(self, report_id: UUID, data: UpdateReportDto) -> ReadReportDto:
        report = await self._get_report_or_404(report_id)

        for field in ["title", "description", "location", "room", "category", "priority", "type", "photo_url"]:
            value = getattr(data, field, None)
            if value is not None:
                setattr(report, field, value)

        updated = await self.report_repo.update(report)
        return ReadReportDto.model_validate(updated)

    async def change_status(
        self, report_id: UUID, new_status: ReportStatus, changed_by: UUID
    ) -> ReadReportDto:
        report = await self._get_report_or_404(report_id)
        old_status = report.status

        allowed = ALLOWED_STATUS_TRANSITIONS.get(old_status, [])
        if new_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot transition from '{old_status.value}' to '{new_status.value}'",
            )

        report.status = new_status
        updated = await self.report_repo.update(report)

        history_entry = ReportStatusHistory(
            report_id=report_id,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
        )
        await self.history_repo.create(history_entry)

        notification = ReportNotification(
            reporter_id=report.reporter_id,
            report_id=report_id,
            report_title=report.title,
            old_status=old_status,
            new_status=new_status,
        )
        await self.notification_repo.create(notification)

        await notification_client.send_push(
            user_id=report.reporter_id,
            title=f'Статус заявки изменён: {report.title}',
            body=f'{old_status.value} → {new_status.value}',
            data={"reportId": str(report_id)},
        )

        return ReadReportDto.model_validate(updated)

    async def force_change_status(
        self, report_id: UUID, new_status: ReportStatus, changed_by: UUID
    ) -> ReadReportDto:
        """Change status without FSM validation — admin only."""
        report = await self._get_report_or_404(report_id)
        old_status = report.status

        report.status = new_status
        updated = await self.report_repo.update(report)

        history_entry = ReportStatusHistory(
            report_id=report_id,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
        )
        await self.history_repo.create(history_entry)

        notification = ReportNotification(
            reporter_id=report.reporter_id,
            report_id=report_id,
            report_title=report.title,
            old_status=old_status,
            new_status=new_status,
        )
        await self.notification_repo.create(notification)

        await notification_client.send_push(
            user_id=report.reporter_id,
            title=f'Статус заявки изменён: {report.title}',
            body=f'{old_status.value} → {new_status.value}',
            data={"reportId": str(report_id)},
        )

        return ReadReportDto.model_validate(updated)

    # --- Notifications ---

    async def get_my_notifications(self, reporter_id: UUID) -> List[ReadNotificationDto]:
        notifications = await self.notification_repo.get_by_reporter(reporter_id)
        return [ReadNotificationDto.model_validate(n) for n in notifications]

    async def mark_notification_read(self, notification_id: UUID, reporter_id: UUID) -> bool:
        return await self.notification_repo.mark_read(notification_id, reporter_id)

    async def mark_all_notifications_read(self, reporter_id: UUID) -> int:
        return await self.notification_repo.mark_all_read(reporter_id)

    async def get_all_reports(
        self,
        limit: int = 50,
        offset: int = 0,
        report_status: Optional[ReportStatus] = None,
        category: Optional[ReportCategory] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[ReadReportListDto]:
        reports = await self.report_repo.get_all(
            limit=limit,
            offset=offset,
            status=report_status,
            category=category,
            date_from=date_from,
            date_to=date_to,
        )
        return [ReadReportListDto.model_validate(r) for r in reports]

    async def get_my_reports(
        self,
        reporter_id: UUID,
        limit: int = 50,
        offset: int = 0,
        report_status: Optional[ReportStatus] = None,
    ) -> List[ReadReportListDto]:
        reports = await self.report_repo.get_by_reporter(
            reporter_id=reporter_id,
            limit=limit,
            offset=offset,
            status=report_status,
        )
        return [ReadReportListDto.model_validate(r) for r in reports]

    # --- Comments ---

    async def add_comment(
        self, report_id: UUID, dto: CreateCommentDto, author_id: UUID
    ) -> ReadCommentDto:
        await self._get_report_or_404(report_id)
        comment = ReportComment(
            report_id=report_id,
            author_id=author_id,
            text=dto.text,
        )
        comment = await self.comment_repo.create(comment)
        return ReadCommentDto.model_validate(comment)

    async def get_comments(self, report_id: UUID) -> List[ReadCommentDto]:
        await self._get_report_or_404(report_id)
        comments = await self.comment_repo.get_by_report_id(report_id)
        return [ReadCommentDto.model_validate(c) for c in comments]

    # --- Status History ---

    async def get_status_history(self, report_id: UUID) -> List[ReadStatusHistoryDto]:
        await self._get_report_or_404(report_id)
        history = await self.history_repo.get_by_report_id(report_id)
        return [ReadStatusHistoryDto.model_validate(h) for h in history]

    # --- Helpers ---

    async def _get_report_or_404(self, report_id: UUID) -> Report:
        report = await self.report_repo.get(report_id)
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report {report_id} not found",
            )
        return report
