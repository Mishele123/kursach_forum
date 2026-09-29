import secrets
from datetime import datetime, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError

from auth.exceptions import (
    UserBanned,
    UserDeleted,
    UsernameAlreadyExists,
    UsernameNotExists,
    UserNotFound,
    WrongPassword,
)
from auth.models import UserModel
from auth.repositories import RedisCache, SessionData, UserRepo

from .auth_dto import (
    UserMeResponse,
    UserRequestCreateDto,
    UserRequestLoginDto,
    UserResponceCreateDto,
    UserResponceLoginDto,
)


def is_user_banned(user: UserModel, now: datetime | None = None) -> bool:
    if user.banned_until is None:
        return False
    now = now or datetime.now(timezone.utc)
    return user.banned_until > now


class CreateUserInteractor:
    def __init__(self, db: UserRepo, password_hasher: PasswordHasher) -> None:
        self._db = db
        self._password_hasher = password_hasher

    async def __call__(self, dto: UserRequestCreateDto) -> UserResponceCreateDto:
        print("create", flush=True)
        existing: UserModel | None = await self._db.read_by_username(dto.username)
        if existing:
            raise UsernameAlreadyExists(dto.username)
        password_hash: str = self._password_hasher.hash(dto.password)

        user: UserModel = await self._db.create(
            UserModel(username=dto.username, password_hash=password_hash)
        )
        print(user)
        return UserResponceCreateDto(username=user.username)


class LoginUserInteractor:
    def __init__(
        self, db: UserRepo, redis: RedisCache, password_hasher: PasswordHasher
    ) -> None:
        self._db = db
        self._redis = redis
        self._password_hasher = password_hasher

    async def __call__(
        self, dto: UserRequestLoginDto, user_agent: str
    ) -> UserResponceLoginDto:
        user: UserModel | None = await self._db.read_by_username(dto.username)
        if user is None:
            raise UserNotFound(dto.username)
        if user.deleted_at is not None:
            raise UserDeleted(user.deleted_at)
        if is_user_banned(user):
            raise UserBanned(user.username, user.banned_until, user.ban_reason)
        try:
            self._password_hasher.verify(user.password_hash, dto.password)
        except (VerifyMismatchError, VerificationError):
            raise WrongPassword()
        if self._password_hasher.check_needs_rehash(user.password_hash):
            new_hash = self._password_hasher.hash(dto.password)
            await self._db.update(user.id, password_hash=new_hash)

        session_id: str = secrets.token_urlsafe(32)
        result: SessionData = await self._redis.create_session(
            session_id,
            user.id,
            user_agent,
        )
        return UserResponceLoginDto(
            username=user.username,
            session_id=session_id,
            max_age=int(
                (result.expires_at - datetime.now(timezone.utc)).total_seconds()
            ),
        )


class UserMeInteractor:
    def __init__(self, db: UserRepo) -> None:
        self._db = db

    async def __call__(self, user_id: int) -> UserMeResponse:
        user: UserModel | None = await self._db.read(user_id)
        if user is None:
            raise UsernameNotExists()
        ban: bool = is_user_banned(user)
        return UserMeResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role.value,
            avatar_url=user.avatar_url,
            bio=user.bio,
            created_at=user.created_at,
            email_verified_at=user.email_verified_at,
            is_banned=ban,
            banned_until=user.banned_until,
            ban_reason=user.ban_reason,
        )
