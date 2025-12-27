from typing import Optional

from pydantic import BaseModel

from domain.models.enums.report_status import ReportStatus
from domain.models.enums.report_type import ReportType


class UpdateReportDto(BaseModel):
    type: Optional[ReportType] = None
    status: Optional[ReportStatus] = None
    isExplicit: Optional[bool] = None
