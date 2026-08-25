import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    headline: Mapped[str | None] = mapped_column(Text)

    bio: Mapped[str | None] = mapped_column(Text)

    location: Mapped[str | None] = mapped_column(Text)

    profile_image_blob_path: Mapped[str | None] = mapped_column(Text)

    years_of_experience: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 1)
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