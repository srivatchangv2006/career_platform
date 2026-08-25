import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class ResumeAnalysis(Base):
    __tablename__ = "resume_analysis"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    resume_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    summary: Mapped[str | None] = mapped_column(Text)

    strengths: Mapped[Any | None] = mapped_column(JSONB)

    weaknesses: Mapped[Any | None] = mapped_column(JSONB)

    extracted_skills: Mapped[Any | None] = mapped_column(JSONB)

    experience_summary: Mapped[Any | None] = mapped_column(JSONB)

    education_summary: Mapped[Any | None] = mapped_column(JSONB)

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