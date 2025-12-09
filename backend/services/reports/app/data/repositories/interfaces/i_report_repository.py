from abc import abstractmethod, ABC
from typing import List
from uuid import UUID

from services.reports.app.domain.models.db.report import Report


class IReportService(ABC):
    @abstractmethod
    async def get_report_by_id(self, report_id: UUID) -> Report:
        pass

    @abstractmethod
    async def get_reports(self, limit: int, offset: int) -> List[Report]:
        pass

    @abstractmethod
    async def create_report(self, report: Report) -> Report:
        pass

    @abstractmethod
    async def delete_report(self, report_id: UUID) -> Report:
        pass

    @abstractmethod
    async def update_report(self, report_id: UUID) -> Report:
        pass
