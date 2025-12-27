from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from domain.models.schemas.create_report import CreateReportDto
from domain.models.schemas.read_report import ReadReportDto
from domain.models.schemas.update_report import UpdateReportDto


class IReportService(ABC):

    @abstractmethod
    def create_report(
            self,
            report_id: UUID,
            dto: CreateReportDto,
            reporter_id: UUID
    ) -> ReadReportDto:
        pass

    @abstractmethod
    async def delete_report(
            self,
            report_id: UUID
    ) -> None:
        pass

    @abstractmethod
    def update_report(
            self,
            report_id: UUID,
            dto: UpdateReportDto
    ) -> ReadReportDto:
        pass

    @abstractmethod
    async def get_report_by_id(
            self,
            report_id: UUID
    ) -> ReadReportDto:
        pass

    @abstractmethod
    async def get_all_reports(
            self,
            limit: int = 50,
            offset: int = 0
    ) -> List[ReadReportDto]:
        pass
