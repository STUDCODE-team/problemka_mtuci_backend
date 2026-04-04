import uuid
from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, func, Text

from common_lib.infrastructure.db.base import Base
from domain.models.enums.report_status import ReportStatus
from domain.models.enums.report_type import ReportType
from domain.models.enums.report_category import ReportCategory
from domain.models.enums.report_priority import ReportPriority


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    title: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    room: Mapped[Optional[str]] = mapped_column(sa.String(100), nullable=True)
    category: Mapped[ReportCategory] = mapped_column(nullable=False)
    priority: Mapped[ReportPriority] = mapped_column(
        default=ReportPriority.MEDIUM, nullable=False
    )
    photo_url: Mapped[Optional[str]] = mapped_column(sa.String(500), nullable=True)

    type: Mapped[ReportType] = mapped_column(nullable=False)
    status: Mapped[ReportStatus] = mapped_column(
        default=ReportStatus.NEW,
        nullable=False,
    )

    reporter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )

    comments = relationship("ReportComment", back_populates="report", lazy="selectin")
    status_history = relationship("ReportStatusHistory", back_populates="report", lazy="selectin")
