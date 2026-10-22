"""Resolve the current account from a session cookie or Bearer token."""
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


security = HTTPBearer(auto_error=False)


async def get_current_user_id(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> int:
    token = credentials.credentials if credentials else request.cookies.get("velo_session", "")
    token_data = await request.app.state.sessions.verify_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data.user_id


CurrentUserId = Annotated[int, Depends(get_current_user_id)]
