import uuid

import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID

from libs.common.domain.reports.models.enums.report_status import ReportStatus
from libs.common.domain.reports.models.enums.report_type import ReportType
from libs.common.infrastructure.db.base import Base


class Report(Base):
    __tablename__ = "reports"
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = sa.Column(sa.Enum(ReportType), nullable=False)
    isExplicit = sa.Column(sa.Boolean, nullable=False, default=False)
    status = sa.Column(
        sa.Enum(ReportStatus),
        default=ReportStatus.DRAFT,
        nullable=False
    )
    reporter_id = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    created_at = sa.Column(
        sa.DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
