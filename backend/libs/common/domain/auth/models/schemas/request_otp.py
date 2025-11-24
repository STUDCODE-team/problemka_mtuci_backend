from pydantic import BaseModel

from libs.common.domain.auth.models.enums.user_roles import UserRole


class RequestOtp(BaseModel):
    email: str
    role: UserRole
