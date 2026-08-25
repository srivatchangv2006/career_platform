import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class JobSkill(Base):
    __tablename__ = "job_skills"

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
    )

    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
    )

    is_required: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
    )

    proficiency_level: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )