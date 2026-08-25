from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class JobRecommendationRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    status: str
    input_context: dict | None
    recommendations: list | None
    model_name: str | None
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime


class JobRecommendationItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    run_id: UUID
    job_id: UUID
    match_score: float | None
    recommendation_reason: str | None
    ranking: int | None
    created_at: datetime


class JobRecommendationAI(BaseModel):
    job_id: UUID
    match_score: float
    recommendation_reason: str
    