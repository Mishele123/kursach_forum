from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class PostCategory(StrEnum):
    """Post categories for Sprint 1 - US3"""
    MAINTENANCE = "обслуживание"  # Maintenance
    UPGRADE = "апгрейд"  # Upgrade
    ROUTE = "маршрут"  # Route
    TRICKS = "трюки"  # Tricks


class Post(BaseModel):
    id: int
    title: str
    text: str
    category: PostCategory
    photo_url: str | None  # Single photo for US3
    author_id: int  # User ID who created the post
    created_at: datetime
    updated_at: datetime
