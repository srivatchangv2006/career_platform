from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ConversationResponse(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime

    other_user_id: UUID | None = None
    other_user_email: str | None = None
    other_user_name: str | None = None
    other_user_role: str | None = None
    other_user_headline: str | None = None
    other_user_company: str | None = None
    other_user_avatar: str | None = None


class ConversationSummaryResponse(BaseModel):
    id: UUID
    other_user_id: UUID
    other_user_email: str
    other_user_name: str | None = None
    other_user_role: str | None = None
    other_user_headline: str | None = None
    other_user_company: str | None = None
    other_user_avatar: str | None = None
    last_message: str | None = None
    last_message_at: datetime | None = None
    unread_count: int
    updated_at: datetime
