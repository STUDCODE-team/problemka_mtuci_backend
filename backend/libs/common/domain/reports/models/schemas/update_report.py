from typing import Optional

from pydantic import BaseModel

from libs.common.domain.reports.models.enums.report_status import ReportStatus
from libs.common.domain.reports.models.enums.report_type import ReportType


class UpdateReportDTO(BaseModel):
    type: Optional[ReportType] = None
    status: Optional[ReportStatus] = None
    isExplicit: Optional[bool] = None
