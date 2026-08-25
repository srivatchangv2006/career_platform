from datetime import date, datetime
from uuid import UUID
from models.job import JobStatus
from pydantic import BaseModel, ConfigDict


class JobCreate(BaseModel):
    company_id: UUID
    title: str
    description: str
    location: str | None = None
    employment_type: str | None = None
    experience_level: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    currency: str = "USD"
    application_deadline: date | None = None


class JobUpdate(BaseModel):
    company_id: UUID | None = None
    title: str | None = None
    description: str | None = None
    location: str | None = None
    employment_type: str | None = None
    experience_level: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    currency: str | None = None
    application_deadline: date | None = None
    status: JobStatus | None = None

class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    posted_by: UUID
    title: str
    description: str
    location: str | None
    employment_type: str | None
    experience_level: str | None
    salary_min: float | None
    salary_max: float | None
    currency: str
    status: JobStatus
    application_deadline: date | None
    created_at: datetime
    updated_at: datetime