from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from auth.controllers import auth_router, register_exception_handlers
from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI
from ioc import (
    AuthProvider,
    ConfigProvider,
    PostgresProvider,
    RedisProvider,
    RepoProvider,
)


def create_container() -> AsyncContainer:
    return make_async_container(
        ConfigProvider(),
        PostgresProvider(),
        RedisProvider(),
        RepoProvider(),
        AuthProvider(),
        FastapiProvider(),
    )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    await app.state.dishka_container.close()


def create_app() -> FastAPI:
    container: AsyncContainer = create_container()
    app: FastAPI = FastAPI(lifespan=lifespan)
    register_exception_handlers(app)
    app.include_router(auth_router)
    setup_dishka(container, app)
    return app


app: FastAPI = create_app()
