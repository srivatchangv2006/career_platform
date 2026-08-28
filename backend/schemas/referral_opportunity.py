from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ReferralOpportunityCreate(BaseModel):
    job_id: UUID | None = None

    opportunity_title: str | None = None
    opportunity_company: str | None = None

    message: str | None = None
    max_referrals: int | None = None


class ReferralOpportunityUpdate(BaseModel):
    message: str | None = None
    max_referrals: int | None = None
    status: str | None = None

    opportunity_title: str | None = None
    opportunity_company: str | None = None


class ReferralOpportunityResponse(BaseModel):
    id: UUID

    posted_by: UUID
    posted_by_name: str
    posted_by_role: str

    job_id: UUID | None = None

    job_title: str
    company_name: str
    job_location: str | None = None

    is_external: bool

    message: str | None

    max_referrals: int | None
    accepted_referrals: int
    remaining_referrals: int | None

    status: str

    created_at: datetime
    updated_at: datetime
