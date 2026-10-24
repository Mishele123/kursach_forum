from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from auth.exceptions import AuthError


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AuthError)
    async def auth_error_handler(request: Request, exc: AuthError):
        content: dict[str, Any] = {
            "error": type(exc).__name__,
            "detail": str(exc),
        }
        if exc.meta:
            content["meta"] = exc.meta
        return JSONResponse(status_code=exc.status_code, content=content)
