from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CommunityPostImageResponse(BaseModel):
    id: UUID
    file_name: str
    content_type: str
    file_size_bytes: int | None


class CommunityPostCreate(BaseModel):
    title: str
    content: str


class CommunityPostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class CommunityPostResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    content: str
    created_at: datetime
    updated_at: datetime