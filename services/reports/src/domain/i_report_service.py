from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from domain.models.enums.report_category import ReportCategory
from domain.models.enums.report_status import ReportStatus
from domain.models.schemas.comment import CreateCommentDto, ReadCommentDto
from domain.models.schemas.create_report import CreateReportDto
from domain.models.schemas.read_report import ReadReportDto, ReadReportListDto
from domain.models.schemas.status_history import ReadStatusHistoryDto
from domain.models.schemas.update_report import UpdateReportDto


class IReportService(ABC):

    @abstractmethod
    async def create_report(self, dto: CreateReportDto, reporter_id: UUID) -> ReadReportDto:
        pass

    @abstractmethod
    async def delete_report(self, report_id: UUID) -> None:
        pass

    @abstractmethod
    async def update_report(self, report_id: UUID, dto: UpdateReportDto) -> ReadReportDto:
        pass

    @abstractmethod
    async def get_report_by_id(self, report_id: UUID) -> ReadReportDto:
        pass

    @abstractmethod
    async def get_all_reports(
        self,
        limit: int = 50,
        offset: int = 0,
        report_status: Optional[ReportStatus] = None,
        category: Optional[ReportCategory] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[ReadReportListDto]:
        pass

    @abstractmethod
    async def get_my_reports(
        self,
        reporter_id: UUID,
        limit: int = 50,
        offset: int = 0,
        report_status: Optional[ReportStatus] = None,
    ) -> List[ReadReportListDto]:
        pass

    @abstractmethod
    async def change_status(
        self, report_id: UUID, new_status: ReportStatus, changed_by: UUID
    ) -> ReadReportDto:
        pass

    @abstractmethod
    async def add_comment(
        self, report_id: UUID, dto: CreateCommentDto, author_id: UUID
    ) -> ReadCommentDto:
        pass

    @abstractmethod
    async def get_comments(self, report_id: UUID) -> List[ReadCommentDto]:
        pass

    @abstractmethod
    async def get_status_history(self, report_id: UUID) -> List[ReadStatusHistoryDto]:
        pass
