import os
from pathlib import Path
from starlette.staticfiles import StaticFiles
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from community.profile import router as profile_router
from community.routes import router as posts_router
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
    upload_dir = Path(os.environ.get("UPLOAD_DIR", str(Path(__file__).resolve().parent.parent / "uploads")))
    upload_dir.mkdir(parents=True, exist_ok=True)
    app.state.upload_dir = upload_dir
    app.mount("/media", StaticFiles(directory=upload_dir), name="media")
    register_exception_handlers(app)
    app.include_router(auth_router)
    app.include_router(posts_router)
    app.include_router(profile_router)
    setup_dishka(container, app)
    return app


app: FastAPI = create_app()
