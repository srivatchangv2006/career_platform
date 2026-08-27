from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class AgentFeedbackCreate(BaseModel):
    interaction_id: UUID | None = None
    task_id: UUID | None = None
    rating: int | None = None
    feedback: str | None = None
    is_helpful: bool | None = None
    metadata: dict[str, Any] | None = None


class AgentFeedbackResponse(BaseModel):
    id: UUID
    user_id: UUID
    interaction_id: UUID | None
    task_id: UUID | None
    rating: int | None
    feedback: str | None
    is_helpful: bool | None
    metadata: dict[str, Any] | None
    created_at: datetime