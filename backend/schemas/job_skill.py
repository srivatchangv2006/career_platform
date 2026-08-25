from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class JobSkillCreate(BaseModel):
    skill_id: UUID
    is_required: bool = True
    proficiency_level: str | None = None


class JobSkillUpdate(BaseModel):
    is_required: bool | None = None
    proficiency_level: str | None = None


class JobSkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job_id: UUID
    skill_id: UUID
    is_required: bool
    proficiency_level: str | None
    created_at: datetime