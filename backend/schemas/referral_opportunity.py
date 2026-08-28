from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ReferralOpportunityCreate(BaseModel):
    job_id: UUID
    message: str | None = None
    max_referrals: int | None = None


class ReferralOpportunityUpdate(BaseModel):
    message: str | None = None
    max_referrals: int | None = None
    status: str | None = None


class ReferralOpportunityResponse(BaseModel):
    id: UUID
    posted_by: UUID
    job_id: UUID
    message: str | None
    max_referrals: int | None
    accepted_referrals: int
    remaining_referrals: int | None
    status: str
    created_at: datetime
    updated_at: datetime