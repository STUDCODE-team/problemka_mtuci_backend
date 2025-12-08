from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from services.reports.app.domain.models.enums.report_status import ReportStatus
from services.reports.app.domain.models.enums.report_type import ReportType


class ReadReportDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    type: ReportType
    is_explicit: bool
    status: ReportStatus
    reporter_id: UUID
    created_at: datetime
