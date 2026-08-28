from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CommunityCommentAuthorResponse(BaseModel):
    user_id: UUID
    role: str
    display_name: str
    headline: str | None = None
    designation: str | None = None
    company_name: str | None = None
    profile_image_blob_path: str | None = None


class CommunityCommentCreate(BaseModel):
    content: str
    parent_comment_id: UUID | None = None


class CommunityCommentUpdate(BaseModel):
    content: str


class CommunityCommentResponse(BaseModel):
    id: UUID
    post_id: UUID
    user_id: UUID
    parent_comment_id: UUID | None
    author: CommunityCommentAuthorResponse
    content: str
    created_at: datetime
    updated_at: datetime
