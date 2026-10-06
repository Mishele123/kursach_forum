from datetime import datetime, timezone

from pydantic import BaseModel

from auth.user_entity import User, UserRole


class CreateUserDto(BaseModel):
    username: str
    password: str = "12345"


def dto_to_user(cls: CreateUserDto) -> User:
    return User(
        id=0,
        email=None,
        username=cls.username,
        password_hash=cls.password,
        role=UserRole.USER,
        avatar_url=None,
        bio=None,
        is_banned=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        last_login_at=None,
        email_verified_at=None,
        last_password_change=datetime.now(timezone.utc),
    )
