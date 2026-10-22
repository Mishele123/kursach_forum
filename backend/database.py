"""Asynchronous database access. PostgreSQL is the application database."""
import os
from contextlib import asynccontextmanager

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from models import Base


class Database:
    def __init__(self, url: str | None = None):
        self.url = url or os.environ.get(
            "DATABASE_URL", "postgresql+asyncpg://velo:velo_local@localhost:15432/velo"
        )
        self.engine = create_async_engine(self.url, poolclass=NullPool)
        self.factory = async_sessionmaker(self.engine, expire_on_commit=False)
        if self.url.startswith("sqlite"):
            # SQLite is only used by isolated offline tests.
            @event.listens_for(self.engine.sync_engine, "connect")
            def foreign_keys(connection, _):
                connection.execute("PRAGMA foreign_keys=ON")

    @asynccontextmanager
    async def session(self):
        async with self.factory.begin() as session:
            yield session

    async def ping(self):
        async with self.engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

    async def create_schema(self):
        """For isolated tests; deployed schemas are managed by Alembic."""
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

    async def reset_test_schema(self):
        async with self.engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
            await connection.run_sync(Base.metadata.create_all)

    async def close(self):
        await self.engine.dispose()
