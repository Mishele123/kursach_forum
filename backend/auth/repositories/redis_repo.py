import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import redis.asyncio as redis

logger = logging.getLogger(__name__)


@dataclass
class SessionData:
    """Session data structure."""

    user_id: int
    expires_at: datetime
    user_agent: str
    session_id: str | None = None


class RedisCache:
    """Redis-based session storage.

    Session Structure:
    1. Individual Sessions:
        - Key: `{prefix}session:{session_id}` (prefix опционален)
        - Value: JSON с `{"user_id": int, "expires_at": iso}`
        - TTL: автоматически истекает в Redis по expires_at

    2. User -> Sessions Mapping:
        - Key: `{prefix}user_sessions:{user_id}`
        - Value: SET из session_id
        - TTL: равен session_ttl_seconds, обновляется при каждом create_session

    3. Sessions ZSET (для cleanup):
        - Key: `{prefix}sessions_expiry`
        - Members: `{user_id}:{session_id}` (для быстрого доступа к user_id)
        - Score: unix timestamp expires_at

    Auto-refresh:
    При вызове get_session, если до истечения осталось меньше refresh_threshold,
    сессия автоматически продлевается на session_ttl_seconds.
    """

    def __init__(
        self,
        session: redis.Redis,
        session_ttl_seconds: int = 60 * 60 * 24 * 30,
        prefix: str = "",
    ) -> None:
        """Initialize Redis session storage.

        :param session: Redis client instance
        :param session_ttl_seconds: Default session TTL in seconds
        :param prefix: Key prefix for namespacing (без завершающего двоеточия)
        """
        self._session = session
        self._session_ttl_seconds = session_ttl_seconds
        self._refresh_threshold = session_ttl_seconds // 2
        self._prefix = f"{prefix}:" if prefix else ""

        self._get_session_script = """
        local key = KEYS[1]
        local now_iso = ARGV[1]

        local data = redis.call('GET', key)
        if not data then
            return nil
        end

        local session = cjson.decode(data)
        if session.expires_at <= now_iso then
            return nil
        end

        return data
        """

    def _get_session_key(self, session_id: str) -> str:
        """Get Redis key for a session."""
        return f"{self._prefix}session:{session_id}"

    def _get_user_sessions_key(self, user_id: int) -> str:
        """Get Redis key for user's sessions set."""
        return f"{self._prefix}user_sessions:{user_id}"

    def _get_sessions_expiry_key(self) -> str:
        """Get Redis key for sessions expiry ZSET."""
        return f"{self._prefix}sessions_expiry"

    def _make_zset_member(self, user_id: int, session_id: str) -> str:
        """Create ZSET member in format 'user_id:session_id'."""
        return f"{user_id}:{session_id}"

    def _parse_zset_member(self, member: str | bytes) -> tuple[int, str]:
        """Parse ZSET member to (user_id, session_id)."""
        if isinstance(member, bytes):
            member = member.decode("utf-8")
        user_id_str, session_id = member.split(":", 1)
        return int(user_id_str), session_id

    async def create_session(
        self, session_id: str, user_id: int, user_agent: str
    ) -> SessionData:
        """Create a new session.

        :param session_id: Unique session identifier
        :param user_id: User ID
        :param user_agent: User Agent
        :raises ValueError: If expires_at is naive or in the past
        """
        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=self._session_ttl_seconds
        )
        if expires_at.tzinfo is None:
            raise ValueError("expires_at must be timezone-aware")

        ttl = int((expires_at - datetime.now(timezone.utc)).total_seconds())
        if ttl <= 0:
            raise ValueError("expires_at must be in the future")

        session_key = self._get_session_key(session_id)
        user_sessions_key = self._get_user_sessions_key(user_id)
        expiry_key = self._get_sessions_expiry_key()

        session_data = {
            "user_id": user_id,
            "expires_at": expires_at.isoformat(),
            "user_agent": user_agent,
        }

        async with self._session.pipeline(transaction=True) as pipe:
            pipe.set(session_key, json.dumps(session_data, ensure_ascii=False), ex=ttl)
            pipe.sadd(user_sessions_key, session_id)
            pipe.expire(user_sessions_key, self._session_ttl_seconds)
            pipe.zadd(
                expiry_key,
                {self._make_zset_member(user_id, session_id): expires_at.timestamp()},
            )
            await pipe.execute()

        return SessionData(user_id, expires_at, user_agent, session_id)

    async def get_session(self, session_id: str) -> SessionData | None:
        """Get session data by session_id.

        Автоматически продлевает сессию, если до истечения осталось меньше
        refresh_threshold (половина TTL по умолчанию).

        :param session_id: Session identifier
        :return: SessionData or None if not found/expired
        """
        session_key = self._get_session_key(session_id)

        try:
            data = await self._session.eval(
                self._get_session_script,
                1,
                session_key,
                datetime.now(timezone.utc).isoformat(),
            )
        except Exception as e:
            logger.error(f"Error executing Lua script for session {session_id}: {e}")
            return None

        if data is None:
            return None

        if isinstance(data, bytes):
            data = data.decode("utf-8")

        try:
            session_dict = json.loads(data)
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted session data for {session_id}: {e}")
            await self.delete_session(session_id)
            return None

        user_id = session_dict["user_id"]
        expires_at = datetime.fromisoformat(session_dict["expires_at"])
        user_agent = session_dict["user_agent"]
        now = datetime.now(timezone.utc)
        time_left = (expires_at - now).total_seconds()

        if time_left < self._refresh_threshold:
            new_expires_at = now + timedelta(seconds=self._session_ttl_seconds)
            await self.refresh_session(session_id, new_expires_at)
            expires_at = new_expires_at

        return SessionData(
            user_id=user_id,
            expires_at=expires_at,
            user_agent=user_agent,
            session_id=session_id,
        )

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session.

        :param session_id: Session identifier
        :return: True if session was deleted, False if not found
        """
        session_key = self._get_session_key(session_id)

        data = await self._session.get(session_key)
        if data is None:
            return False

        if isinstance(data, bytes):
            data = data.decode("utf-8")

        try:
            session_dict = json.loads(data)
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted session data for {session_id}: {e}")
            await self._session.delete(session_key)
            return False

        user_id = session_dict["user_id"]
        user_sessions_key = self._get_user_sessions_key(user_id)
        expiry_key = self._get_sessions_expiry_key()

        async with self._session.pipeline(transaction=True) as pipe:
            pipe.delete(session_key)
            pipe.srem(user_sessions_key, session_id)
            pipe.zrem(expiry_key, self._make_zset_member(user_id, session_id))
            await pipe.execute()

        return True

    async def get_user_sessions(self, user_id: int) -> list[SessionData]:
        """Get all active sessions for a user.

        :param user_id: User ID
        :return: List of SessionData objects
        """
        user_sessions_key = self._get_user_sessions_key(user_id)
        session_ids_raw = await self._session.smembers(user_sessions_key)

        session_ids = []
        for sid in session_ids_raw:
            if isinstance(sid, bytes):
                sid = sid.decode("utf-8")
            session_ids.append(sid)

        if not session_ids:
            return []

        async with self._session.pipeline(transaction=False) as pipe:
            for session_id in session_ids:
                pipe.get(self._get_session_key(session_id))
            results = await pipe.execute()

        sessions = []
        expired_ids = []

        for session_id, data in zip(session_ids, results):
            if data is None:
                expired_ids.append(session_id)
                continue

            if isinstance(data, bytes):
                data = data.decode("utf-8")

            try:
                session_dict = json.loads(data)
            except json.JSONDecodeError as e:
                logger.error(f"Corrupted session data for {session_id}: {e}")
                expired_ids.append(session_id)
                continue

            expires_at = datetime.fromisoformat(session_dict["expires_at"])

            if expires_at <= datetime.now(timezone.utc):
                expired_ids.append(session_id)
                continue

            sessions.append(
                SessionData(
                    user_id=user_id,
                    expires_at=expires_at,
                    user_agent=session_dict.get("user_agent"),
                    session_id=session_id,
                )
            )

        if expired_ids:
            await self._session.srem(user_sessions_key, *expired_ids)

        return sessions

    async def delete_user_sessions(self, user_id: int) -> int:
        """Delete all sessions for a user.

        :param user_id: User ID
        :return: Number of sessions deleted
        """
        user_sessions_key = self._get_user_sessions_key(user_id)
        session_ids_raw = await self._session.smembers(user_sessions_key)

        session_ids = []
        for sid in session_ids_raw:
            if isinstance(sid, bytes):
                sid = sid.decode("utf-8")
            session_ids.append(sid)

        if not session_ids:
            return 0

        expiry_key = self._get_sessions_expiry_key()

        async with self._session.pipeline(transaction=True) as pipe:
            for session_id in session_ids:
                session_key = self._get_session_key(session_id)
                pipe.delete(session_key)
                pipe.zrem(expiry_key, self._make_zset_member(user_id, session_id))
            pipe.delete(user_sessions_key)
            await pipe.execute()

        return len(session_ids)

    async def refresh_session(self, session_id: str, new_expires_at: datetime) -> bool:
        """Refresh session expiration time.

        Атомарно обновляет TTL и expires_at без удаления сессии.

        :param session_id: Session identifier
        :param new_expires_at: New expiration datetime (must be timezone-aware)
        :return: True if refreshed, False if session not found
        :raises ValueError: If new_expires_at is naive or in the past
        """
        if new_expires_at.tzinfo is None:
            raise ValueError("new_expires_at must be timezone-aware")

        ttl = int((new_expires_at - datetime.now(timezone.utc)).total_seconds())
        if ttl <= 0:
            raise ValueError("new_expires_at must be in the future")

        session_key = self._get_session_key(session_id)

        data = await self._session.get(session_key)
        if data is None:
            return False

        if isinstance(data, bytes):
            data = data.decode("utf-8")

        try:
            session_dict = json.loads(data)
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted session data for {session_id}: {e}")
            return False

        try:
            user_id = session_dict["user_id"]
        except KeyError:
            logger.error(f"Session {session_id} missing user_id")
            return False
        session_dict["expires_at"] = new_expires_at.isoformat()

        expiry_key = self._get_sessions_expiry_key()

        async with self._session.pipeline(transaction=True) as pipe:
            pipe.set(session_key, json.dumps(session_dict, ensure_ascii=False), ex=ttl)
            pipe.zadd(
                expiry_key,
                {
                    self._make_zset_member(
                        user_id, session_id
                    ): new_expires_at.timestamp()
                },
            )
            await pipe.execute()

        return True

    async def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions.

        Удаляет протухшие сессии из всех структур данных:
        - session:{id}
        - user_sessions:{user_id}
        - sessions_expiry ZSET

        :return: Number of sessions cleaned up
        """
        expiry_key = self._get_sessions_expiry_key()
        now = datetime.now(timezone.utc).timestamp()

        expired_members_raw = await self._session.zrangebyscore(expiry_key, 0, now)

        if not expired_members_raw:
            return 0

        expired_sessions = []
        for member in expired_members_raw:
            try:
                user_id, session_id = self._parse_zset_member(member)
                expired_sessions.append((user_id, session_id, member))
            except (ValueError, IndexError) as e:
                logger.error(f"Invalid ZSET member format: {member}, error: {e}")
                continue

        if not expired_sessions:
            return 0

        async with self._session.pipeline(transaction=False) as pipe:
            for user_id, session_id, member in expired_sessions:
                session_key = self._get_session_key(session_id)
                user_sessions_key = self._get_user_sessions_key(user_id)

                pipe.delete(session_key)
                pipe.srem(user_sessions_key, session_id)
                pipe.zrem(expiry_key, member)

            await pipe.execute()

        return len(expired_sessions)
