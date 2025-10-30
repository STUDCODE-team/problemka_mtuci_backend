import uuid

import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.dialects.postgresql.base import UUID

from libs.common.domain.auth.models.enums.user_roles import UserRole
from libs.common.infrastructure.db.base import Base


class User(Base):
    __tablename__ = "users"
    id = sa.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = sa.Column(sa.String(255), unique=True, index=True, nullable=False)
    is_active = sa.Column(sa.Boolean, default=True)
    verified_at = sa.Column(sa.DateTime(timezone=True), nullable=True)
    created_at = sa.Column(sa.DateTime(timezone=True), server_default=func.now())
    role = sa.Column(sa.Enum(UserRole), default=UserRole.USER, nullable=False)
