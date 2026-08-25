from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProfileBase(BaseModel):
    full_name: str
    headline: str | None = None
    bio: str | None = None
    location: str | None = None
    profile_image_blob_path: str | None = None
    years_of_experience: float | None = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    headline: str | None = None
    bio: str | None = None
    location: str | None = None
    profile_image_blob_path: str | None = None
    years_of_experience: float | None = None


class ProfileResponse(ProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime