from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from schemas.network import NetworkUserResponse


class UserFollowResponse(BaseModel):
    follower_id: UUID
    following_id: UUID
    created_at: datetime

    follower: NetworkUserResponse | None = None
    following: NetworkUserResponse | None = None
