import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class UserSkill(Base):
    __tablename__ = "user_skills"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
    )

    skill_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
    )

    proficiency: Mapped[str | None] = mapped_column(Text)

    years_experience: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 1)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    