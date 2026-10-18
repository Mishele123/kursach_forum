import os
from pathlib import Path
from starlette.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from config import WebConfig
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from community.bikes import router as bikes_router
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
    web = WebConfig()
    app.state.web_config = web

    @app.middleware("http")
    async def check_origin(request, call_next):
        origin = request.headers.get("origin")
        if request.method not in {"GET", "HEAD", "OPTIONS"} and origin:
            own_origin = str(request.base_url).rstrip("/")
            if origin not in {*web.allowed_origins, own_origin}:
                return JSONResponse({"detail": "Недопустимый источник запроса"}, status_code=403)
        return await call_next(request)

    app.add_middleware(CORSMiddleware, allow_origins=web.allowed_origins,
                       allow_credentials=True, allow_methods=["GET", "POST", "PATCH", "PUT"],
                       allow_headers=["Content-Type"])
    upload_dir = Path(os.environ.get("UPLOAD_DIR", str(Path(__file__).resolve().parent.parent / "uploads")))
    upload_dir.mkdir(parents=True, exist_ok=True)
    app.state.upload_dir = upload_dir
    app.mount("/media", StaticFiles(directory=upload_dir), name="media")
    register_exception_handlers(app)
    app.include_router(auth_router)
    app.include_router(posts_router)
    app.include_router(profile_router)
    app.include_router(bikes_router)
    setup_dishka(container, app)
    return app


app: FastAPI = create_app()
