from typing import Optional

from pydantic import BaseModel, Field

from domain.models.enums.report_category import ReportCategory
from domain.models.enums.report_priority import ReportPriority
from domain.models.enums.report_type import ReportType


class CreateReportDto(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1, max_length=255)
    room: Optional[str] = Field(None, max_length=100)
    category: ReportCategory
    priority: ReportPriority = ReportPriority.MEDIUM
    type: ReportType = ReportType.REPORT
    photo_url: Optional[str] = None
