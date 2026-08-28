from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CommunityVoteCreate(BaseModel):
    vote: str


class CommunityVoteResponse(BaseModel):
    id: UUID
    user_id: UUID
    post_id: UUID | None
    comment_id: UUID | None
    vote: str
    created_at: datetime
