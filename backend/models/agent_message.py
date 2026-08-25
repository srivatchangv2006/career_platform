import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class AgentMessage(Base):
    __tablename__ = "agent_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agent_tasks.id", ondelete="CASCADE"),
        nullable=True,
    )

    sender_agent: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    receiver_agent: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    message_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default="PENDING",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
    )

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )