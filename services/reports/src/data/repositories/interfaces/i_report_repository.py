from abc import abstractmethod, ABC
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from domain.models.db.report import Report
from domain.models.enums.report_category import ReportCategory
from domain.models.enums.report_status import ReportStatus


class IReportRepository(ABC):
    @abstractmethod
    async def get(self, report_id: UUID) -> Optional[Report]:
        pass

    @abstractmethod
    async def get_all(
        self,
        limit: int,
        offset: int,
        status: Optional[ReportStatus] = None,
        category: Optional[ReportCategory] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> List[Report]:
        pass

    @abstractmethod
    async def get_by_reporter(
        self,
        reporter_id: UUID,
        limit: int,
        offset: int,
        status: Optional[ReportStatus] = None,
    ) -> List[Report]:
        pass

    @abstractmethod
    async def create(self, report: Report) -> Report:
        pass

    @abstractmethod
    async def delete(self, report: Report) -> None:
        pass

    @abstractmethod
    async def update(self, report: Report) -> Report:
        pass
