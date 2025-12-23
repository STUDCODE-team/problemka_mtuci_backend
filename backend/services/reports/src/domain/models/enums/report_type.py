from enum import Enum


class ReportType(str, Enum):
    REPORT = "report"
    LOST = "lost"
    SUGGESTION = "suggestion"
