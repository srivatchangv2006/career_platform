import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


from models.base import Base


class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    interviewer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True)
    )

    interview_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    duration_minutes: Mapped[int | None] = mapped_column(
        Integer
    )

    meeting_url: Mapped[str | None] = mapped_column(Text)

    location: Mapped[str | None] = mapped_column(Text)

    notes: Mapped[str | None] = mapped_column(Text)

    status: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default="SCHEDULED",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )