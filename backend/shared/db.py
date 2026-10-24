from config import PostgresConfig
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    pass


def new_session_maker(config: PostgresConfig) -> async_sessionmaker[AsyncSession]:

    database_url = f"postgresql+asyncpg://{config.user}:{config.password}@{config.host}:{config.port}/{config.db}"

    engine = create_async_engine(
        database_url,
        pool_size=15,
        max_overflow=15,
        connect_args={
            "timeout": 5,
        },
        echo=False,
    )

    return async_sessionmaker(
        engine, class_=AsyncSession, autoflush=False, expire_on_commit=False
    )
