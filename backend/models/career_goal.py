import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class CareerGoal(Base):
    __tablename__ = "career_goals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    goal_title: Mapped[str] = mapped_column(Text, nullable=False)
    target_role: Mapped[str | None] = mapped_column(Text)
    target_industry: Mapped[str | None] = mapped_column(Text)
    target_location: Mapped[str | None] = mapped_column(Text)
    target_company: Mapped[str | None] = mapped_column(Text)
    target_timeline: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
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