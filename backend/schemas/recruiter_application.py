from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class RecruiterCandidateProfile(BaseModel):
    id: UUID
    full_name: str
    headline: str | None
    bio: str | None
    location: str | None
    years_of_experience: float | None


class RecruiterCandidateSkill(BaseModel):
    skill_id: UUID
    proficiency: str | None
    years_experience: float | None


class RecruiterCandidate(BaseModel):
    id: UUID
    email: str
    profile: RecruiterCandidateProfile | None
    skills: list[RecruiterCandidateSkill]


class RecruiterApplicationDetails(BaseModel):
    id: UUID
    job_id: UUID
    user_id: UUID
    resume_id: UUID | None
    status: str
    cover_letter: str | None
    applied_at: datetime
    updated_at: datetime


class RecruiterJobSummary(BaseModel):
    id: UUID
    company_id: UUID
    title: str
    description: str
    location: str | None
    employment_type: str | None
    experience_level: str | None
    salary_min: float | None
    salary_max: float | None
    currency: str
    status: str


class RecruiterResumeSummary(BaseModel):
    id: UUID
    file_name: str
    content_type: str | None
    file_size_bytes: int | None
    is_primary: bool


class RecruiterApplicationDetailResponse(BaseModel):
    application: RecruiterApplicationDetails
    candidate: RecruiterCandidate
    job: RecruiterJobSummary
    resume: RecruiterResumeSummary | None

class RecruiterResumeDownloadResponse(BaseModel):
    resume_id: UUID
    file_name: str
    content_type: str | None
class RecruiterApplicationAnswer(BaseModel):
    id: UUID
    question_id: UUID
    question: str
    question_type: str
    is_required: bool
    display_order: int
    answer: str | None
