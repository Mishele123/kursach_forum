from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, StringConstraints

Username = Annotated[
    str,
    StringConstraints(
        min_length=3,
        max_length=50,
        strip_whitespace=True,
        pattern=r"^[a-zA-Z0-9_]+$",
    ),
]

Password = Annotated[str, StringConstraints(min_length=8, max_length=20)]


class UserRequestCreateDto(BaseModel):
    username: Username
    password: Password


class UserResponceCreateDto(BaseModel):
    username: str


class UserRequestLoginDto(BaseModel):
    username: Username
    password: Password
    remember_me: bool = False


class UserResponceLoginDto(BaseModel):
    username: str
    session_id: str
    max_age: int


class UserMeResponse(BaseModel):
    id: int
    username: str
    email: str | None
    role: str
    avatar_url: str | None
    bio: str | None
    created_at: datetime
    email_verified_at: datetime | None
    is_banned: bool = False
    banned_until: datetime | None = None
    ban_reason: str | None = None
