import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class ApplicationStatus(str, Enum):
    SAVED = "SAVED"
    APPLIED = "APPLIED"
    SCREENING = "SCREENING"
    ASSESSMENT = "ASSESSMENT"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    resume_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True)
    )

    status: Mapped[ApplicationStatus] = mapped_column(
        SQLEnum(
            ApplicationStatus,
            name="application_status",
            create_type=False,
        ),
        nullable=False,
        server_default="APPLIED",
    )

    cover_letter: Mapped[str | None] = mapped_column(Text)

    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )