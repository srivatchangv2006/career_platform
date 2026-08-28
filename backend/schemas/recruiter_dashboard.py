from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class RecruiterApplicationListItem(BaseModel):
    id: UUID
    job_id: UUID
    candidate_id: UUID
    candidate_email: str
    candidate_name: str | None
    job_title: str
    status: str
    resume_id: UUID | None
    applied_at: datetime
    updated_at: datetime


class RecruiterApplicationStatusCounts(BaseModel):
    APPLIED: int = 0
    SCREENING: int = 0
    ASSESSMENT: int = 0
    INTERVIEW: int = 0
    OFFER: int = 0
    REJECTED: int = 0
    WITHDRAWN: int = 0


class RecruiterDashboardResponse(BaseModel):
    total_jobs: int
    open_jobs: int
    total_applications: int
    applications_by_status: RecruiterApplicationStatusCounts
    upcoming_interviews: int
