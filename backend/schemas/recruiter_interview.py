from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class RecruiterInterviewCreate(BaseModel):
    application_id: UUID
    interviewer_id: UUID | None = None
    interview_type: str
    scheduled_at: datetime | None = None
    duration_minutes: int | None = None
    meeting_url: str | None = None
    location: str | None = None
    notes: str | None = None
    status: str = "SCHEDULED"


class RecruiterInterviewUpdate(BaseModel):
    interviewer_id: UUID | None = None
    interview_type: str | None = None
    scheduled_at: datetime | None = None
    duration_minutes: int | None = None
    meeting_url: str | None = None
    location: str | None = None
    notes: str | None = None
    status: str | None = None
