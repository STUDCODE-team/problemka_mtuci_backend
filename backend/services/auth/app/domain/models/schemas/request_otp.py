from pydantic import BaseModel

from services.auth.app.domain.models.enums.user_roles import UserRole


class RequestOtp(BaseModel):
    email: str
    role: UserRole
