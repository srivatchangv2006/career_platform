from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AgentTaskStepCreate(BaseModel):
    step_name: str
    step_order: int = 0
    agent_name: str | None = None
    status: str = "PENDING"
    input_data: dict | None = None


class AgentTaskStepUpdate(BaseModel):
    step_name: str | None = None
    step_order: int | None = None
    agent_name: str | None = None
    status: str | None = None
    input_data: dict | None = None
    output_data: dict | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class AgentTaskStepResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    task_id: UUID
    step_name: str
    step_order: int
    agent_name: str | None
    status: str
    input_data: dict | None
    output_data: dict | None
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime