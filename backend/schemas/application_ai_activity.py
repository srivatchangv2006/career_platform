from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class AIActivityTask(BaseModel):
    id: UUID
    task_type: str
    status: str
    input_data: dict[str, Any] | None
    output_data: dict[str, Any] | None
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime


class AIActivityStep(BaseModel):
    id: UUID
    task_id: UUID
    step_name: str
    step_order: int
    agent_name: str | None
    status: str
    input_data: dict[str, Any] | None
    output_data: dict[str, Any] | None
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime


class AIActivityMessage(BaseModel):
    id: UUID
    task_id: UUID | None
    sender_agent: str
    receiver_agent: str
    message_type: str
    payload: dict[str, Any]
    status: str
    created_at: datetime
    processed_at: datetime | None


class AIActivityInteraction(BaseModel):
    id: UUID
    interaction_type: str
    model_name: str | None
    input_text: str | None
    output_text: str | None
    metadata: dict[str, Any] | None
    created_at: datetime


class ApplicationAIActivityResponse(BaseModel):
    application_id: UUID
    tasks: list[AIActivityTask]
    steps: list[AIActivityStep]
    messages: list[AIActivityMessage]
    interactions: list[AIActivityInteraction]