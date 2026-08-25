from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SkillGapAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    job_id: UUID
    matched_skills: list
    missing_skills: list
    recommendations: list
    overall_match_score: float | None
    created_at: datetime
    updated_at: datetime