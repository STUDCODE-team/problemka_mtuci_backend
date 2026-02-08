from enum import Enum


class ReportStatus(Enum):
    DRAFT = 'draft'
    PENDING = 'pending'
    NEED_REVIEW = 'need_review'
    PUBLISHED = 'published'
    RESOLVED = 'resolved'
    REJECTED = 'rejected'
    DUPLICATED = 'duplicated'
