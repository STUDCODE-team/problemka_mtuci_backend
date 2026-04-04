from pydantic import BaseModel, EmailStr

from domain.models.enums.user_roles import UserRole


class RequestOtp(BaseModel):
    email: EmailStr
    role: UserRole
