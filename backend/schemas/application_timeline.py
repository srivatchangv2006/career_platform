from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ApplicationTimelineEvent(BaseModel):
    id: UUID
    event_type: str
    title: str
    description: str | None = None
    status: str | None = None
    created_at: datetime


class ApplicationTimelineResponse(BaseModel):
    application_id: UUID
    events: list[ApplicationTimelineEvent]