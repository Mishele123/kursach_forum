from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import uvicorn
from auth.http import router
from dishka import make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from ioc import AuthProvider

container = make_async_container(AuthProvider())


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield await app.state.dishka_container_close()


def get_fastapi_app() -> FastAPI:
    fastapi_app = FastAPI()
    fastapi_app.include_router(router)
    setup_dishka(container, fastapi_app)
    return fastapi_app


def get_app() -> FastAPI:
    fastapi_app = get_fastapi_app()
    return fastapi_app


if __name__ == "__main__":
    uvicorn.run(get_app(), host="0.0.0.0", port=8000, lifespan="on")
