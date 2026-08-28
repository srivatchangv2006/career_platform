from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UserFollowResponse(BaseModel):
    follower_id: UUID
    following_id: UUID
    created_at: datetime
