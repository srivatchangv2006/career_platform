from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EducationBase(BaseModel):
    institution: str
    degree: str | None = None
    field_of_study: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None


class EducationCreate(EducationBase):
    pass


class EducationUpdate(BaseModel):
    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None


class EducationResponse(EducationBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime