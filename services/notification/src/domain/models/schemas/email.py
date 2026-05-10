from pydantic import BaseModel


class SendOtpEmailDto(BaseModel):
    to_email: str
    otp: str
