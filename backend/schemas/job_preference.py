from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class JobPreferenceCreate(BaseModel):
    preferred_roles: list[str] | None = None
    preferred_locations: list[str] | None = None
    preferred_employment_types: list[str] | None = None
    preferred_experience_levels: list[str] | None = None
    minimum_salary: float | None = None
    preferred_currency: str = "USD"
    remote_preferred: bool = False


class JobPreferenceUpdate(BaseModel):
    preferred_roles: list[str] | None = None
    preferred_locations: list[str] | None = None
    preferred_employment_types: list[str] | None = None
    preferred_experience_levels: list[str] | None = None
    minimum_salary: float | None = None
    preferred_currency: str | None = None
    remote_preferred: bool | None = None


class JobPreferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    preferred_roles: list[str] | None
    preferred_locations: list[str] | None
    preferred_employment_types: list[str] | None
    preferred_experience_levels: list[str] | None
    minimum_salary: float | None
    preferred_currency: str
    remote_preferred: bool
    created_at: datetime
    updated_at: datetime