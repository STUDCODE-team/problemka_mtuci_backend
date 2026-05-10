from typing import Optional

from pydantic import BaseModel, Field

from domain.models.enums.report_category import ReportCategory
from domain.models.enums.report_priority import ReportPriority
from domain.models.enums.report_type import ReportType


class UpdateReportDto(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    location: Optional[str] = Field(None, min_length=1, max_length=255)
    room: Optional[str] = Field(None, max_length=100)
    category: Optional[ReportCategory] = None
    priority: Optional[ReportPriority] = None
    type: Optional[ReportType] = None
    photo_url: Optional[str] = None
