import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Numeric, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class AgentMemory(Base):
    __tablename__ = "agent_memory"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    memory_type: Mapped[str] = mapped_column(Text, nullable=False)

    memory_key: Mapped[str | None] = mapped_column(Text, nullable=True)

    memory_value: Mapped[dict] = mapped_column(JSONB, nullable=False)

    source: Mapped[str | None] = mapped_column(Text, nullable=True)

    confidence_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default="now()",
    )