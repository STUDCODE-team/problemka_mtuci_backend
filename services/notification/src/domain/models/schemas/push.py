from uuid import UUID

from pydantic import BaseModel


class PushSubscriptionDto(BaseModel):
    endpoint: str
    p256dh: str
    auth: str


class SendPushDto(BaseModel):
    user_id: UUID
    title: str
    body: str
    data: dict | None = None
