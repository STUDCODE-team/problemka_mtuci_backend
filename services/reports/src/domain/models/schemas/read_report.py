from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from domain.models.enums.report_category import ReportCategory
from domain.models.enums.report_priority import ReportPriority
from domain.models.enums.report_status import ReportStatus
from domain.models.enums.report_type import ReportType


class ReadReportDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str
    location: str
    room: Optional[str]
    category: ReportCategory
    priority: ReportPriority
    type: ReportType
    status: ReportStatus
    reporter_id: UUID
    photo_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]


class ReadReportListDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    location: str
    category: ReportCategory
    status: ReportStatus
    priority: ReportPriority
    created_at: datetime
