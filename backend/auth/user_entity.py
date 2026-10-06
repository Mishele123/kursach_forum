from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel


class UserRole(StrEnum):
    USER = "USER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"


class User(BaseModel):
    id: int
    email: (
        str | None
    )  # чекать на уникальность + при регистрации будет логин и пароль поэтому может быть None
    username: str  # чекать уникальность
    password_hash: str
    role: UserRole  # "user" | "moderator" | "admin"
    avatar_url: str | None
    bio: str | None
    is_banned: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: datetime | None
    email_verified_at: (
        datetime | None
    )  # будем ли мы слать сообщения по почте? надо обсудить
    last_password_change: datetime  # это чтобы можно было сессию сбросить при восстановлении доступа к аккаунту
