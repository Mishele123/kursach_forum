from datetime import datetime
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, StringConstraints, Field, model_validator

Category = Literal['maintenance', 'upgrade', 'route', 'tricks']
Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=10000)]


PlaceName = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]


class PostPlace(BaseModel):
    model_config = ConfigDict(extra='forbid')
    latitude: float = Field(ge=-90, le=90, allow_inf_nan=False)
    longitude: float = Field(ge=-180, le=180, allow_inf_nan=False)
    name: PlaceName | None = None


class PostCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: Title
    text: Text
    category: Category
    place: PostPlace | None = None


class AuthorResponse(BaseModel):
    id: int
    username: str
    avatar_url: str | None = None


class PhotoResponse(BaseModel):
    id: int
    url: str


class PostResponse(BaseModel):
    id: int
    author: AuthorResponse
    title: str
    text: str
    category: Category
    place: PostPlace | None = None
    like_count: int = 0
    liked_by_me: bool = False
    photos: list[PhotoResponse] = Field(default_factory=list)
    photo_url: str | None
    created_at: datetime


class FeedResponse(BaseModel):
    items: list[PostResponse]
    next_cursor: str | None
