from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class AIInteractionCreate(BaseModel):
    interaction_type: str
    input_text: str | None = None
    output_text: str | None = None
    model_name: str | None = None
    metadata: dict[str, Any] | None = None


class AIInteractionResponse(BaseModel):
    id: UUID
    user_id: UUID
    interaction_type: str
    input_text: str | None
    output_text: str | None
    model_name: str | None
    metadata: dict[str, Any] | None
    created_at: datetime