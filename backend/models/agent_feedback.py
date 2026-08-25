import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class AgentFeedback(Base):
    __tablename__ = "agent_feedback"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    interaction_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_interactions.id", ondelete="SET NULL"),
        nullable=True,
    )

    task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agent_tasks.id", ondelete="SET NULL"),
        nullable=True,
    )

    rating: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    is_helpful: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    metadata_: Mapped[dict | None] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
    )