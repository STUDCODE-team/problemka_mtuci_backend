from pydantic import BaseModel, EmailStr


class VerifyOtp(BaseModel):
    email: EmailStr
    code: str
