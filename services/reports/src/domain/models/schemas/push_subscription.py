from pydantic import BaseModel


class PushSubscriptionDto(BaseModel):
    endpoint: str
    p256dh: str
    auth: str
