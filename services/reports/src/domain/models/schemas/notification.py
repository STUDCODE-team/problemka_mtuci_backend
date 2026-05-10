from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from domain.models.enums.report_status import ReportStatus


class ReadNotificationDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    reporter_id: UUID
    report_id: UUID
    report_title: str
    old_status: ReportStatus
    new_status: ReportStatus
    is_read: bool
    created_at: datetime
