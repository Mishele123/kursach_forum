from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import UserModel


class UserRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def read(self, id: int) -> UserModel | None:
        stmt = select(UserModel).where(
            UserModel.id == id, UserModel.deleted_at.is_(None)
        )
        return await self._session.scalar(stmt)

    async def read_by_username(self, username: str) -> UserModel | None:
        stmt = select(UserModel).where(
            UserModel.username == username, UserModel.deleted_at.is_(None)
        )
        return await self._session.scalar(stmt)

    async def read_by_email(self, email: str) -> UserModel | None:
        stmt = select(UserModel).where(
            UserModel.email == email, UserModel.deleted_at.is_(None)
        )
        return await self._session.scalar(stmt)

    async def create(self, user: UserModel) -> UserModel:
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def update(self, id: int, **kwargs) -> bool:
        if not kwargs:
            return False
        result = await self._session.execute(
            update(UserModel)
            .where(UserModel.id == id, UserModel.deleted_at.is_(None))
            .values(kwargs)
        )
        return result.rowcount > 0

    async def delete(self, id: int) -> bool:
        result = await self._session.execute(
            update(UserModel)
            .where(UserModel.id == id, UserModel.deleted_at.is_(None))
            .values(deleted_at=datetime.now(timezone.utc))
        )
        return result.rowcount > 0
