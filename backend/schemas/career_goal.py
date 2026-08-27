from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CareerGoalCreate(BaseModel):
    goal_title: str
    target_role: str | None = None
    target_industry: str | None = None
    target_location: str | None = None
    target_company: str | None = None
    target_timeline: str | None = None
    description: str | None = None
    is_active: bool = True


class CareerGoalUpdate(BaseModel):
    goal_title: str | None = None
    target_role: str | None = None
    target_industry: str | None = None
    target_location: str | None = None
    target_company: str | None = None
    target_timeline: str | None = None
    description: str | None = None
    is_active: bool | None = None


class CareerGoalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    goal_title: str
    target_role: str | None
    target_industry: str | None
    target_location: str | None
    target_company: str | None
    target_timeline: str | None
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CareerRecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    goal_id: UUID | None
    job_id: UUID | None
    recommendation_type: str
    title: str
    description: str | None
    priority: str | None
    metadata: dict[str, Any] | None
    is_completed: bool
    created_at: datetime
    updated_at: datetime