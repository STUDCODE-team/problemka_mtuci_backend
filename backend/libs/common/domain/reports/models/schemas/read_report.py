from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from libs.common.domain.reports.models.enums.report_status import ReportStatus
from libs.common.domain.reports.models.enums.report_type import ReportType


class ReadReportDto(BaseModel):
    id: UUID
    type: ReportType
    status: ReportStatus
    isExplicit: bool
    reporter_id: UUID
    created_at: datetime
