import uuid
from datetime import datetime

from sqlalchemy import DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    website_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    logo_blob_path: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    industry: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    company_size: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    location: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
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