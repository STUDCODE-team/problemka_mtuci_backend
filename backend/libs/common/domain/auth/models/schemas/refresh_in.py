from pydantic import BaseModel


class RefreshIn(BaseModel):
    refresh_token: str
