from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AgentMemoryCreate(BaseModel):
    memory_type: str
    memory_key: str | None = None
    memory_value: dict
    source: str | None = None
    confidence_score: float | None = None


class AgentMemoryUpdate(BaseModel):
    memory_type: str | None = None
    memory_key: str | None = None
    memory_value: dict | None = None
    source: str | None = None
    confidence_score: float | None = None


class AgentMemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    memory_type: str
    memory_key: str | None
    memory_value: dict
    source: str | None
    confidence_score: float | None
    created_at: datetime
    updated_at: datetime


class AgentMemorySearchResult(BaseModel):
    id: UUID
    memory_type: str
    memory_key: str | None
    memory_value: dict
    source: str | None
    confidence_score: float | None
    similarity: float
    created_at: datetime