import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Experience(Base):
    __tablename__ = "experience"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    company_name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    job_title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    employment_type: Mapped[str | None] = mapped_column(Text)

    location: Mapped[str | None] = mapped_column(Text)

    start_date: Mapped[date | None] = mapped_column(Date)

    end_date: Mapped[date | None] = mapped_column(Date)

    description: Mapped[str | None] = mapped_column(Text)

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