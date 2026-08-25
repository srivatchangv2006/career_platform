import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class InterviewPreparation(Base):
    __tablename__ = "interview_preparations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    preparation_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    questions: Mapped[Any | None] = mapped_column(JSONB)

    suggested_answers: Mapped[Any | None] = mapped_column(JSONB)

    strengths: Mapped[Any | None] = mapped_column(JSONB)

    improvement_areas: Mapped[Any | None] = mapped_column(JSONB)

    recommendations: Mapped[Any | None] = mapped_column(JSONB)

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