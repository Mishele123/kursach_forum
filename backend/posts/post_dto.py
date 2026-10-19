from datetime import datetime

from pydantic import BaseModel

from posts.post_entity import PostCategory


class CreatePostDto(BaseModel):
    """DTO for creating a post (US3)"""
    title: str
    text: str
    category: PostCategory
    photo_url: str | None = None  # Optional photo


class PostResponseDto(BaseModel):
    """DTO for returning post info"""
    id: int
    title: str
    text: str
    category: PostCategory
    photo_url: str | None
    author_id: int
    author_username: str | None  # For display in feed
    created_at: datetime
