"""Redis sessions: only token digests are stored; TTL enforces expiration."""
import hashlib
import secrets
from datetime import timedelta

from pydantic import BaseModel
from redis.asyncio import Redis

from auth.user_storage import SqlAlchemyUserRepository
from database import Database

SESSION_SECONDS = 7 * 24 * 60 * 60


class TokenData(BaseModel):
    user_id: int
    username: str


def digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class SessionService:
    def __init__(self, database: Database, redis: Redis):
        self.database = database
        self.redis = redis

    async def create_access_token(self, user_id: int, expires_delta: timedelta | None = None) -> str:
        token = secrets.token_urlsafe(48)
        seconds = int(expires_delta.total_seconds()) if expires_delta is not None else SESSION_SECONDS
        if seconds > 0:
            await self.redis.set("velo:session:" + digest(token), str(user_id), ex=seconds)
        return token

    async def verify_token(self, token: str) -> TokenData | None:
        if not token:
            return None
        value = await self.redis.get("velo:session:" + digest(token))
        if value is None:
            return None
        user = await SqlAlchemyUserRepository(self.database).read(int(value))
        if user is None or user.is_banned:
            return None
        return TokenData(user_id=user.id, username=user.username)

    async def revoke_token(self, token: str) -> None:
        await self.redis.delete("velo:session:" + digest(token))
