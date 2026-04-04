from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from domain.models.enums.report_status import ReportStatus


class ReadStatusHistoryDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    report_id: UUID
    old_status: ReportStatus
    new_status: ReportStatus
    changed_by: UUID
    changed_at: datetime


class ChangeStatusDto(BaseModel):
    status: ReportStatus
