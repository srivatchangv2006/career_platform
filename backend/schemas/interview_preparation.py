from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InterviewPreparationResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: UUID
    application_id: UUID
    user_id: UUID
    preparation_type: str
    questions: list[Any] | None
    suggested_answers: list[Any] | None
    strengths: list[Any] | None
    improvement_areas: list[Any] | None
    recommendations: list[Any] | None
    created_at: datetime
    updated_at: datetime