# models/user.py
import uuid
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from libs.common.infrastructure.db.base import Base
from services.auth.src.domain.models.enums.user_roles import UserRole


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        sa.String(255), unique=True, index=True, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    verified_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=func.now()
    )
    role: Mapped[UserRole] = mapped_column(
        sa.Enum(UserRole), default=UserRole.USER, nullable=False
    )
