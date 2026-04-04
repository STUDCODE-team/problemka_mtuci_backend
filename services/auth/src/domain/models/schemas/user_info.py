from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from domain.models.enums.user_roles import UserRole


class UserInfoDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
