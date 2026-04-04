from enum import Enum


class ReportStatus(str, Enum):
    NEW = 'new'
    IN_PROGRESS = 'in_progress'
    RESOLVED = 'resolved'
    REJECTED = 'rejected'


# Допустимые переходы статусов (FSM)
ALLOWED_STATUS_TRANSITIONS: dict[ReportStatus, list[ReportStatus]] = {
    ReportStatus.NEW: [ReportStatus.IN_PROGRESS, ReportStatus.REJECTED],
    ReportStatus.IN_PROGRESS: [ReportStatus.RESOLVED, ReportStatus.REJECTED],
    ReportStatus.RESOLVED: [],
    ReportStatus.REJECTED: [],
}
