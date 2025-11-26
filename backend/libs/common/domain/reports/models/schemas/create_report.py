from pydantic import BaseModel

from libs.common.domain.reports.models.enums.report_type import ReportType


class CreateReportDto(BaseModel):
    type: ReportType
    isExplicit: bool = False
