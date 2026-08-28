from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ConnectionCreate(BaseModel):
    receiver_id: UUID


class ConnectionUpdate(BaseModel):
    status: str


class ConnectionResponse(BaseModel):
    id: UUID
    requester_id: UUID
    receiver_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
