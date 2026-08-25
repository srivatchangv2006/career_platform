import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    file_name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    blob_container: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    blob_path: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    content_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default="application/pdf",
    )

    file_size_bytes: Mapped[int | None] = mapped_column(
        BigInteger
    )

    is_primary: Mapped[bool] = mapped_column(
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