from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


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
    content: str
    created_at: datetime
    updated_at: datetime
