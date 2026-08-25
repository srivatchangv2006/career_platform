import uuid
from datetime import datetime

from sqlalchemy import DateTime, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class AIInteraction(Base):
    __tablename__ = "ai_interactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )

    interaction_type: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    input_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    output_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    model_name: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    metadata_: Mapped[dict | None] = mapped_column(
        "metadata",
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
    )