import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SQLEnum, Numeric, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class JobStatus(str, Enum):
    DRAFT = "DRAFT"
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    EXPIRED = "EXPIRED"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    posted_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    location: Mapped[str | None] = mapped_column(Text)

    employment_type: Mapped[str | None] = mapped_column(Text)

    experience_level: Mapped[str | None] = mapped_column(Text)

    salary_min: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2)
    )

    salary_max: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2)
    )

    currency: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default="USD",
    )

    status: Mapped[JobStatus] = mapped_column(
        SQLEnum(
            JobStatus,
            name="job_status",
            create_type=False,
        ),
        nullable=False,
        server_default="DRAFT",
    )

    application_deadline: Mapped[date | None] = mapped_column(
        Date
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