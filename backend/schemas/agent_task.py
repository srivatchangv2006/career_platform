from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AgentTaskCreate(BaseModel):
    task_type: str
    input_data: dict | None = None


class AgentTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    task_type: str
    status: str
    input_data: dict | None
    output_data: dict | None
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime