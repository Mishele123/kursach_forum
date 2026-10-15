from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, CheckConstraint, Index, func
from sqlalchemy.orm import Mapped, mapped_column
from shared import Base


class Post(Base):
    __tablename__ = 'posts'
    __table_args__ = (
        CheckConstraint("category IN ('maintenance', 'upgrade', 'route', 'tricks')", name='ck_posts_category'),
        Index('ix_posts_created_id', 'created_at', 'id'),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    title: Mapped[str] = mapped_column(String(200))
    text: Mapped[str] = mapped_column(String(10000))
    category: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
