from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from auth.http import router as auth_router
from posts.http import router as posts_router
from bikes.http import router as bikes_router
from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from ioc import AuthProvider, PostProvider, BikeProvider

container = make_async_container(AuthProvider(), PostProvider(), BikeProvider())


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield await app.state.dishka_container_close()


def get_fastapi_app() -> FastAPI:
    fastapi_app = FastAPI(
        title="Cycling Social Network API",
        description="Backend API for Sprint 1",
        version="1.0.0"
    )
    
    # Root endpoint
    @fastapi_app.get("/", tags=["root"])
    async def root():
        """Welcome page with API information"""
        return {
            "message": "🚴 Welcome to Cycling Social Network API",
            "version": "1.0.0",
            "docs": "/docs",
            "redoc": "/redoc",
            "endpoints": {
                "auth": {
                    "register": "POST /auth/register",
                    "login": "POST /auth/login",
                    "profile": "GET /auth/me",
                    "update_profile": "PUT /auth/me"
                },
                "posts": {
                    "create": "POST /posts",
                    "list": "GET /posts",
                    "detail": "GET /posts/{id}"
                },
                "bikes": {
                    "add": "POST /bikes",
                    "my_bikes": "GET /bikes/my-bikes"
                }
            }
        }
    
    # Include all routers
    fastapi_app.include_router(auth_router, prefix="/auth")
    fastapi_app.include_router(posts_router)
    fastapi_app.include_router(bikes_router)
    
    setup_dishka(container, fastapi_app)
    return fastapi_app


def get_app() -> FastAPI:
    fastapi_app = get_fastapi_app()
    return fastapi_app


if __name__ == "__main__":
    uvicorn.run(get_app(), host="0.0.0.0", port=8000, lifespan="on")
