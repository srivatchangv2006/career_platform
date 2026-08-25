from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SkillCreate(BaseModel):
    name: str
    slug: str


class SkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    created_at: datetime


class UserSkillCreate(BaseModel):
    skill_id: UUID
    proficiency: str | None = None
    years_experience: float | None = None


class UserSkillUpdate(BaseModel):
    proficiency: str | None = None
    years_experience: float | None = None


class UserSkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    skill_id: UUID
    proficiency: str | None
    years_experience: float | None
    created_at: datetime