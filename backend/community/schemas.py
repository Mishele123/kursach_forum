from datetime import datetime
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, StringConstraints

Category = Literal['maintenance', 'upgrade', 'route', 'tricks']
Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Text = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=10000)]


class PostCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    title: Title
    text: Text
    category: Category


class AuthorResponse(BaseModel):
    id: int
    username: str


class PostResponse(BaseModel):
    id: int
    author: AuthorResponse
    title: str
    text: str
    category: Category
    photo_url: str | None
    created_at: datetime


class FeedResponse(BaseModel):
    items: list[PostResponse]
    next_cursor: str | None
