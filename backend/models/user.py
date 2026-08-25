import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, String, Text, func
from sqlalchemy.dialects.postgresql import CITEXT, UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class UserRole(str, Enum):
    CANDIDATE = "CANDIDATE"
    RECRUITER = "RECRUITER"
    ADMIN = "ADMIN"


class UserStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
    )

    email: Mapped[str] = mapped_column(
        CITEXT,
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    role: Mapped[UserRole] = mapped_column(
        SQLEnum(
            UserRole,
            name="user_role",
            create_type=False,
        ),
        nullable=False,
        server_default="CANDIDATE",
    )

    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(
            UserStatus,
            name="user_status",
            create_type=False,
        ),
        nullable=False,
        server_default="ACTIVE",
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