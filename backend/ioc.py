from collections.abc import AsyncIterator

import redis.asyncio as redis
from argon2 import PasswordHasher
from auth.infra import new_redis_client
from auth.repositories import RedisCache, UserRepo
from auth.services import CreateUserInteractor, LoginUserInteractor
from config import Config, PostgresConfig, RedisConfig
from dishka import Provider, Scope, provide
from shared import new_session_maker
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class ConfigProvider(Provider):
    @provide(scope=Scope.APP)
    def get_config(self) -> Config:
        return Config()

    @provide(scope=Scope.APP)
    def get_postgres_config(self, config: Config) -> PostgresConfig:
        return config.postgres

    @provide(scope=Scope.APP)
    def get_redis_config(self, config: Config) -> RedisConfig:
        return config.redis


class PostgresProvider(Provider):
    @provide(scope=Scope.APP)
    def get_session_maker(
        self, config: PostgresConfig
    ) -> async_sessionmaker[AsyncSession]:
        return new_session_maker(config)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, session_maker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterator[AsyncSession]:
        async with session_maker() as session:
            yield session
            await session.commit()


class RedisProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_redis_client(self, config: RedisConfig) -> AsyncIterator[redis.Redis]:
        client = new_redis_client(config)
        yield client
        await client.aclose()

    @provide(scope=Scope.APP)
    def get_redis_cache(self, client: redis.Redis, config: RedisConfig) -> RedisCache:
        return RedisCache(client, config.session_ttl_seconds)


class RepoProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_user_repo(self, session: AsyncSession) -> UserRepo:
        return UserRepo(session)


class AuthProvider(Provider):
    @provide(scope=Scope.APP)
    def get_password_hasher(self) -> PasswordHasher:
        return PasswordHasher()

    @provide(scope=Scope.REQUEST)
    def get_create_user_interactor(
        self,
        db: UserRepo,
        password_hasher: PasswordHasher,
    ) -> CreateUserInteractor:
        return CreateUserInteractor(db, password_hasher)

    @provide(scope=Scope.REQUEST)
    def get_login_interactor(
        self,
        db: UserRepo,
        redis: RedisCache,
        password_hasher: PasswordHasher,
    ) -> LoginUserInteractor:
        return LoginUserInteractor(db, redis, password_hasher)
