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


class ApplicationStatusHistory(Base):
    __tablename__ = "application_status_history"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    application_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    status: Mapped[ApplicationStatus] = mapped_column(
        SQLEnum(
            ApplicationStatus,
            name="application_status",
            create_type=False,
        ),
        nullable=False,
    )

    changed_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True)
    )

    notes: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )