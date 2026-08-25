from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ResumeAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    resume_id: UUID
    user_id: UUID
    summary: str | None
    strengths: Any | None
    weaknesses: Any | None
    extracted_skills: Any | None
    experience_summary: Any | None
    education_summary: Any | None
    recommendations: Any | None
    created_at: datetime
    updated_at: datetime