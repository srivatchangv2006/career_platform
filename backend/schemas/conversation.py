from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ConversationResponse(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime


class ConversationSummaryResponse(BaseModel):
    id: UUID
    other_user_id: UUID
    other_user_email: str
    last_message: str | None = None
    last_message_at: datetime | None = None
    unread_count: int
    updated_at: datetime