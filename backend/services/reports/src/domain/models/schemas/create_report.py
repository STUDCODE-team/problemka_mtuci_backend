from pydantic import BaseModel

from domain.models.enums.report_type import ReportType


class CreateReportDto(BaseModel):
    type: ReportType
    isExplicit: bool = False
