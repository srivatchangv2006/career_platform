from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class RecruiterProfileCreate(BaseModel):
    company_id: UUID
    designation: str | None = None
    bio: str | None = None


class RecruiterProfileUpdate(BaseModel):
    company_id: UUID | None = None
    designation: str | None = None
    bio: str | None = None


class RecruiterProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    company_id: UUID
    designation: str | None
    bio: str | None
    created_at: datetime
    updated_at: datetime
