import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from common_lib.infrastructure.db.base import Base


class UserRoleRecord(Base):
    """Отдельная таблица для управления ролями с поддержкой admin/manager/user."""
    __tablename__ = "user_roles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True
    )
    role: Mapped[str] = mapped_column(
        sa.String(50), nullable=False, default="user"
    )
