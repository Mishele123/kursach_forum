"""SQLAlchemy user repository with indexed, normalized identity lookup."""
from fastapi import HTTPException
from sqlalchemy import select, update, delete
from sqlalchemy.exc import IntegrityError

from database import Database
from models import UserRow
from auth.user_entity import User
from auth.user_interfaces import UserRepository


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, database: Database):
        self.database = database

    async def read_all(self) -> list[User]:
        async with self.database.session() as session:
            rows = (await session.scalars(select(UserRow))).all()
            return [User.model_validate(row, from_attributes=True) for row in rows]

    async def read(self, id: int) -> User | None:
        async with self.database.session() as session:
            row = await session.get(UserRow, id)
            return User.model_validate(row, from_attributes=True) if row else None

    async def find_by_login(self, identity: str) -> User | None:
        key = identity.strip().casefold()
        field = UserRow.email_key if "@" in key else UserRow.username_key
        async with self.database.session() as session:
            row = await session.scalar(select(UserRow).where(field == key))
            return User.model_validate(row, from_attributes=True) if row else None

    async def create(self, entity: User) -> User:
        values = entity.model_dump(exclude={"id"})
        row = UserRow(**values, username_key=entity.username.casefold(), email_key=entity.email.casefold() if entity.email else None)
        try:
            async with self.database.session() as session:
                session.add(row)
                await session.flush()
                entity.id = row.id
            return entity
        except IntegrityError as error:
            raise HTTPException(409, "Имя пользователя или email уже заняты") from error

    async def update(self, entity: User) -> bool:
        values = entity.model_dump(exclude={"id"})
        values["username_key"] = entity.username.casefold()
        try:
            async with self.database.session() as session:
                result = await session.execute(update(UserRow).where(UserRow.id == entity.id).values(**values))
                return result.rowcount > 0
        except IntegrityError as error:
            raise HTTPException(409, "Имя пользователя уже занято") from error

    async def delete(self, id: int) -> bool:
        async with self.database.session() as session:
            result = await session.execute(delete(UserRow).where(UserRow.id == id))
            return result.rowcount > 0
