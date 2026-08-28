from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ReferralRequestCreate(BaseModel):
    resume_id: UUID | None = None
    message: str | None = None


class ReferralRequestUpdate(BaseModel):
    status: str


class ReferralResponse(BaseModel):
    id: UUID

    opportunity_id: UUID

    requester_id: UUID
    requester_name: str

    resume_id: UUID | None = None
    resume_name: str | None = None

    message: str | None

    status: str

    created_at: datetime
    updated_at: datetime
