from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ApplicationAnswerCreate(BaseModel):
    question_id: UUID
    answer: str | None = None


class ApplicationAnswerUpdate(BaseModel):
    answer: str | None = None


class ApplicationAnswerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    application_id: UUID
    question_id: UUID
    answer: str | None
    created_at: datetime
    updated_at: datetime