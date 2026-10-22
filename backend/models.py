"""Relational SQLAlchemy models for Sprint 1."""
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UserRow(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50))
    username_key: Mapped[str] = mapped_column(String(150), unique=True)
    email: Mapped[str | None] = mapped_column(String(254))
    email_key: Mapped[str | None] = mapped_column(String(254), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="USER")
    avatar_url: Mapped[str | None] = mapped_column(Text)
    bio: Mapped[str | None] = mapped_column(String(1000))
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    city: Mapped[str | None] = mapped_column(String(100))
    discipline: Mapped[str | None] = mapped_column(String(100))
    interests: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_password_change: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PostRow(Base):
    __tablename__ = "posts"
    __table_args__ = (
        CheckConstraint("length(trim(title)) > 0", name="post_title_not_blank"),
        CheckConstraint("length(trim(text)) > 0", name="post_text_not_blank"),
        Index("ix_posts_created_id", "created_at", "id"),
        Index("ix_posts_category_created", "category", "created_at"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    text: Mapped[str] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(30))
    photo_url: Mapped[str | None] = mapped_column(Text)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class BikeRow(Base):
    __tablename__ = "bikes"
    __table_args__ = (
        CheckConstraint("length(trim(brand)) > 0", name="bike_brand_not_blank"),
        CheckConstraint("length(trim(model)) > 0", name="bike_model_not_blank"),
        CheckConstraint("year >= 1800", name="bike_year_min"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    brand: Mapped[str] = mapped_column(String(100))
    model: Mapped[str] = mapped_column(String(100))
    year: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
