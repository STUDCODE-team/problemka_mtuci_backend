import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from common_lib.infrastructure.db.base import Base
from domain.models.enums.report_status import ReportStatus
from domain.models.enums.report_type import ReportType


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    type: Mapped[ReportType] = mapped_column(nullable=False)
    is_explicit: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=False, kw_only=True,
                                              name="isExplicit")
    status: Mapped[ReportStatus] = mapped_column(
        default=ReportStatus.DRAFT,
        nullable=False,
    )

    reporter_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
