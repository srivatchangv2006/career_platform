import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class CareerRecommendation(Base):
    __tablename__ = "career_recommendations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    goal_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True)
    )

    job_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True)
    )

    recommendation_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(Text)
    priority: Mapped[str | None] = mapped_column(Text)

    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB, nullable=True)
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
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