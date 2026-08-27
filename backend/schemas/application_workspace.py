from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class WorkspaceJob(BaseModel):
    id: UUID
    title: str
    description: str
    location: str | None
    employment_type: str | None
    experience_level: str | None
    salary_min: float | None
    salary_max: float | None
    currency: str


class WorkspaceResume(BaseModel):
    id: UUID
    file_name: str
    content_type: str | None
    file_size_bytes: int | None
    is_primary: bool


class WorkspaceSkillGap(BaseModel):
    id: UUID
    job_id: UUID
    matched_skills: list
    missing_skills: list
    recommendations: list
    overall_match_score: float | None


class WorkspaceInterviewPreparation(BaseModel):
    id: UUID
    preparation_type: str
    questions: list | None
    suggested_answers: list | None
    strengths: list | None
    improvement_areas: list | None
    recommendations: list | None


class WorkspaceInterview(BaseModel):
    id: UUID
    interview_type: str
    scheduled_at: datetime | None
    duration_minutes: int | None
    meeting_url: str | None
    location: str | None
    notes: str | None
    status: str
    preparation: WorkspaceInterviewPreparation | None


class WorkspaceApplication(BaseModel):
    id: UUID
    user_id: UUID
    job_id: UUID
    resume_id: UUID | None
    status: str
    cover_letter: str | None
    applied_at: datetime | None
    updated_at: datetime


class ApplicationWorkspaceResponse(BaseModel):
    application: WorkspaceApplication
    job: WorkspaceJob
    resume: WorkspaceResume | None
    skill_gap: WorkspaceSkillGap | None
    interviews: list[WorkspaceInterview]