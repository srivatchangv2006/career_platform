import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Numeric, Text, func
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column


from models.base import Base


class JobPreference(Base):
    __tablename__ = "job_preferences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        unique=True,
    )

    preferred_roles: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text)
    )

    preferred_locations: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text)
    )

    preferred_employment_types: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text)
    )

    preferred_experience_levels: Mapped[list[str] | None] = mapped_column(
        ARRAY(Text)
    )

    minimum_salary: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2)
    )

    preferred_currency: Mapped[str | None] = mapped_column(
        Text,
        default="USD",
        server_default="USD",
    )

    remote_preferred: Mapped[bool] = mapped_column(
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