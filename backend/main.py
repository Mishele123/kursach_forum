"""FastAPI application and lifecycle for PostgreSQL/Redis resources."""
import os
from contextlib import asynccontextmanager

from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy.exc import SQLAlchemyError

from auth.http import router as auth_router
from auth.session import SessionService
from bikes.http import router as bikes_router
from database import Database
from ioc import AppProvider
from posts.http import router as posts_router
from shared.http import router as upload_router
from shared.upload import UPLOAD_DIR


def get_app(database_url: str | None = None, redis_client=None) -> FastAPI:
    database = Database(database_url)
    redis = redis_client if redis_client is not None else Redis.from_url(
        os.environ.get("REDIS_URL", "redis://localhost:16379/0"), decode_responses=True,
        socket_connect_timeout=5, socket_timeout=5,
    )
    container = make_async_container(AppProvider(), context={Database: database})

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        try:
            await database.ping()
            await redis.ping()
            yield
        finally:
            await container.close()
            await redis.aclose()
            await database.close()

    app = FastAPI(title="velo. API", description="Сообщество велосипедистов — Спринт 1", version="1.0.0", lifespan=lifespan)
    app.state.database = database
    app.state.redis = redis
    app.state.sessions = SessionService(database, redis)
    origins = os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
    app.add_middleware(CORSMiddleware, allow_origins=origins.split(","), allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
    app.include_router(auth_router, prefix="/auth")
    app.include_router(posts_router)
    app.include_router(bikes_router)
    app.include_router(upload_router)
    setup_dishka(container, app)

    @app.exception_handler(RedisError)
    @app.exception_handler(SQLAlchemyError)
    async def infrastructure_unavailable(request: Request, error: Exception):
        return JSONResponse(status_code=503, content={"detail": "Сервис временно недоступен. Попробуйте позже."})

    @app.get("/health", tags=["system"])
    async def health():
        await database.ping()
        await redis.ping()
        return {"status": "ok", "database": "postgresql" if database.url.startswith("postgresql") else "test", "sessions": "redis"}

    @app.get("/", tags=["system"])
    async def root():
        return {"name": "velo. API", "docs": "/docs", "health": "/health"}

    return app


app = get_app()
