from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ExperienceBase(BaseModel):
    company_name: str
    job_title: str
    employment_type: str | None = None
    location: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None


class ExperienceCreate(ExperienceBase):
    pass


class ExperienceUpdate(BaseModel):
    company_name: str | None = None
    job_title: str | None = None
    employment_type: str | None = None
    location: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None


class ExperienceResponse(ExperienceBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime