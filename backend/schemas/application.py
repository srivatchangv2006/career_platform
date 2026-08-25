from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ApplicationCreate(BaseModel):
    job_id: UUID
    resume_id: UUID | None = None
    cover_letter: str | None = None


class ApplicationUpdate(BaseModel):
    resume_id: UUID | None = None
    cover_letter: str | None = None


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    job_id: UUID
    user_id: UUID
    resume_id: UUID | None
    status: str
    cover_letter: str | None
    applied_at: datetime
    updated_at: datetime