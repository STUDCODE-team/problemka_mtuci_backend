from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CreateCommentDto(BaseModel):
    text: str = Field(..., min_length=1)


class ReadCommentDto(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    report_id: UUID
    author_id: UUID
    text: str
    created_at: datetime
