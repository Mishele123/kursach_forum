import enum
from datetime import datetime

from shared import Base
from sqlalchemy import DateTime, ForeignKey, func, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import CITEXT, JSONB
from sqlalchemy.orm import Mapped, mapped_column


class UserRole(str, enum.Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str | None] = mapped_column(CITEXT(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(CITEXT(255), unique=True)
    # display_username: Mapped[str | None] = mapped_column(CITEXT(255))
    password_hash: Mapped[str | None]
    role: Mapped[UserRole] = mapped_column(
        SAEnum(
            UserRole,
            name="user_role",
            native_enum=True,
            values_callable=lambda x: [e.value for e in x],
        ),
        server_default=UserRole.USER.value,
    )
    avatar_url: Mapped[str | None]
    city: Mapped[str | None] = mapped_column(String(100))
    discipline: Mapped[str | None] = mapped_column(String(100))
    interests: Mapped[list[str]] = mapped_column(JSONB, default=list, server_default="[]")
    bio: Mapped[str | None]
    banned_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ban_reason: Mapped[str | None]
    banned_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_password_change: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
