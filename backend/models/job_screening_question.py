import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class JobScreeningQuestion(Base):
    __tablename__ = "job_screening_questions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    question: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    question_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default="TEXT",
    )

    is_required: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
    )

    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )