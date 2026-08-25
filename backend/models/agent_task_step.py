import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class AgentTaskStep(Base):
    __tablename__ = "agent_task_steps"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    step_name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    step_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )

    agent_name: Mapped[str | None] = mapped_column(Text)

    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default="PENDING",
    )

    input_data: Mapped[Any | None] = mapped_column(JSONB)
    output_data: Mapped[Any | None] = mapped_column(JSONB)
    error_message: Mapped[str | None] = mapped_column(Text)

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )