from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, CheckConstraint, Index, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column
from shared import Base


class Post(Base):
    __tablename__ = 'posts'
    __table_args__ = (
        CheckConstraint("category IN ('maintenance', 'upgrade', 'route', 'tricks')", name='ck_posts_category'),
        Index('ix_posts_created_id', 'created_at', 'id'),
        CheckConstraint('(place_latitude IS NULL AND place_longitude IS NULL AND place_name IS NULL) OR (place_latitude BETWEEN -90 AND 90 AND place_longitude BETWEEN -180 AND 180)', name='ck_posts_place'),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    title: Mapped[str] = mapped_column(String(200))
    text: Mapped[str] = mapped_column(String(10000))
    category: Mapped[str] = mapped_column(String(20))
    place_latitude: Mapped[float | None] = mapped_column(Numeric(10, 7, asdecimal=False))
    place_longitude: Mapped[float | None] = mapped_column(Numeric(10, 7, asdecimal=False))
    place_name: Mapped[str | None] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Bike(Base):
    __tablename__ = 'bikes'
    __table_args__ = (CheckConstraint('year >= 1800 AND year <= 2200', name='ck_bikes_year'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), index=True)
    brand: Mapped[str] = mapped_column(String(100))
    model: Mapped[str] = mapped_column(String(100))
    year: Mapped[int]
    photo_filename: Mapped[str | None] = mapped_column(String(64))

    @property
    def photo_url(self) -> str | None:
        return f"/media/{self.photo_filename}" if self.photo_filename else None


class Comment(Base):
    __tablename__ = 'comments'
    __table_args__ = (Index('ix_comments_post_id_id', 'post_id', 'id'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey('posts.id', ondelete='CASCADE'))
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    text: Mapped[str] = mapped_column(String(3000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PostLike(Base):
    __tablename__ = 'post_likes'
    post_id: Mapped[int] = mapped_column(ForeignKey('posts.id', ondelete='CASCADE'), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True, index=True)


class PostPhoto(Base):
    __tablename__ = 'post_photos'
    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey('posts.id', ondelete='CASCADE'), index=True)
    filename: Mapped[str] = mapped_column(String(64), unique=True)
