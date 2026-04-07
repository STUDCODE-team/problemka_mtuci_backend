from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UserInfoDto(BaseModel):
    id: UUID
    email: str
    role: str
    is_active: bool
    created_at: datetime
