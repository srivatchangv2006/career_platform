from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from models.application import ApplicationStatus


class ApplicationStatusHistoryCreate(BaseModel):
    status: ApplicationStatus
    notes: str | None = None


class ApplicationStatusHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    application_id: UUID
    status: ApplicationStatus
    changed_by: UUID | None
    notes: str | None
    created_at: datetime