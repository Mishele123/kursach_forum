from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from auth.http import router as auth_router
from posts.http import router as posts_router
from bikes.http import router as bikes_router
from shared.http import router as shared_router
from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
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
    
    # Add CORS middleware
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",  # Vite dev server
            "http://127.0.0.1:5173",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "null"  # For file:// protocol
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Create uploads directory if it doesn't exist
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(exist_ok=True)
    
    # Serve uploaded files statically
    fastapi_app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
    
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
                    "profile": "GET /auth/me (requires token)",
                    "update_profile": "PUT /auth/me (requires token)"
                },
                "posts": {
                    "create": "POST /posts (requires token)",
                    "list": "GET /posts",
                    "detail": "GET /posts/{id}"
                },
                "bikes": {
                    "add": "POST /bikes (requires token)",
                    "my_bikes": "GET /bikes/my-bikes (requires token)"
                },
                "uploads": {
                    "upload": "POST /uploads (requires token)",
                    "info": "GET /uploads/info"
                }
            },
            "authentication": {
                "type": "Bearer JWT",
                "header": "Authorization: Bearer <token>",
                "get_token": "POST /auth/login with username and password"
            }
        }
    
    # Include all routers
    fastapi_app.include_router(auth_router, prefix="/auth")
    fastapi_app.include_router(posts_router)
    fastapi_app.include_router(bikes_router)
    fastapi_app.include_router(shared_router)
    
    setup_dishka(container, fastapi_app)
    return fastapi_app


def get_app() -> FastAPI:
    fastapi_app = get_fastapi_app()
    return fastapi_app


# Create app instance for uvicorn
app = get_app()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, lifespan="on")
