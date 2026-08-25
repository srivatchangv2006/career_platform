from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AgentMessageCreate(BaseModel):
    task_id: UUID | None = None
    sender_agent: str
    receiver_agent: str
    message_type: str
    payload: dict
    status: str = "PENDING"


class AgentMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    task_id: UUID | None
    sender_agent: str
    receiver_agent: str
    message_type: str
    payload: dict
    status: str
    created_at: datetime
    processed_at: datetime | None