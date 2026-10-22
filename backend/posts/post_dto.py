from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from posts.post_entity import PostCategory


class CreatePostDto(BaseModel):
    """DTO for creating a post (US3)"""
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str = Field(..., min_length=1, max_length=200)
    text: str = Field(..., min_length=1, max_length=5000)
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
    author_avatar_url: str | None = None
    created_at: datetime
