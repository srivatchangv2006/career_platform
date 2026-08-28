from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CommunityPostImageResponse(BaseModel):
    id: UUID
    file_name: str
    content_type: str
    file_size_bytes: int | None


class CommunityPostAuthorResponse(BaseModel):
    user_id: UUID
    role: str
    display_name: str
    headline: str | None = None
    bio: str | None = None
    location: str | None = None
    profile_image_blob_path: str | None = None
    designation: str | None = None
    company_name: str | None = None


class CommunityPostCreate(BaseModel):
    title: str
    content: str


class CommunityPostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class CommunityPostResponse(BaseModel):
    id: UUID
    user_id: UUID
    author: CommunityPostAuthorResponse
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    upvotes: int = 0
    downvotes: int = 0
    user_vote: str | None = None
