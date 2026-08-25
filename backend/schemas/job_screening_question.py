from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class JobScreeningQuestionCreate(BaseModel):
    question: str
    question_type: str = "TEXT"
    is_required: bool = True
    display_order: int = 0


class JobScreeningQuestionUpdate(BaseModel):
    question: str | None = None
    question_type: str | None = None
    is_required: bool | None = None
    display_order: int | None = None


class JobScreeningQuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    question: str
    question_type: str
    is_required: bool
    display_order: int
    created_at: datetime