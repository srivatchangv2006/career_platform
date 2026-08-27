from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class InterviewCreate(BaseModel):
    application_id: UUID
    interviewer_id: UUID | None = None
    interview_type: str
    scheduled_at: datetime | None = None
    duration_minutes: int | None = None
    meeting_url: str | None = None
    location: str | None = None
    notes: str | None = None
    status: str = "SCHEDULED"


class InterviewUpdate(BaseModel):
    interviewer_id: UUID | None = None
    interview_type: str | None = None
    scheduled_at: datetime | None = None
    duration_minutes: int | None = None
    meeting_url: str | None = None
    location: str | None = None
    notes: str | None = None
    status: str | None = None


class InterviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    application_id: UUID
    interviewer_id: UUID | None
    interview_type: str
    scheduled_at: datetime | None
    duration_minutes: int | None
    meeting_url: str | None
    location: str | None
    notes: str | None
    status: str
    created_at: datetime
    updated_at: datetime