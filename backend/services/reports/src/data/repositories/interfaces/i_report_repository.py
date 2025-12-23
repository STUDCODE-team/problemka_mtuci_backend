from abc import abstractmethod, ABC
from typing import List
from uuid import UUID

from services.reports.src.domain.models.db.report import Report


class IReportRepository(ABC):
    @abstractmethod
    async def get(self, report_id: UUID) -> Report:
        pass

    @abstractmethod
    async def get_all(self, limit: int, offset: int) -> List[Report]:
        pass

    @abstractmethod
    async def create(self, report: Report) -> Report:
        pass

    @abstractmethod
    async def delete(self, report_id: UUID) -> Report:
        pass

    @abstractmethod
    async def update(self, report_id: UUID) -> Report:
        pass
