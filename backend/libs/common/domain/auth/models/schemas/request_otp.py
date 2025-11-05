from pydantic import BaseModel


class RequestOtp(BaseModel):
    email: str
