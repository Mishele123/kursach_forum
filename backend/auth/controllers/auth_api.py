from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, Request, Response, status

from sqlalchemy.ext.asyncio import AsyncSession
from auth.current_user import current_user
from auth.repositories import RedisCache
from community.profile import ProfileResponse
from pydantic import BaseModel, ConfigDict
from datetime import datetime, timezone
from sqlalchemy import select
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError
from starlette.concurrency import run_in_threadpool
from auth.models import UserModel
from auth.services.auth_dto import Password

from auth.services import (
    CreateUserInteractor,
    LoginUserInteractor,
    UserRequestCreateDto,
    UserRequestLoginDto,
    UserResponceCreateDto,
    UserResponceLoginDto,
)

class LoginResponse(BaseModel):
    username: str


auth_router = APIRouter(prefix="/auth", route_class=DishkaRoute)


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    dto: UserRequestCreateDto, interactor: FromDishka[CreateUserInteractor], db: FromDishka[AsyncSession]
) -> UserResponceCreateDto:
    result = await interactor(dto)
    await db.commit()
    return result


@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    dto: UserRequestLoginDto,
    request: Request,
    response: Response,
    interactor: FromDishka[LoginUserInteractor],
) -> LoginResponse:

    user_agent: str | None = request.headers.get("user-agent")
    if not user_agent or not user_agent.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User-Agent header is required",
        )

    result: UserResponceLoginDto = await interactor(dto, user_agent)
    response.set_cookie(
        key="session_id",
        value=result.session_id,
        httponly=True,
        secure=request.app.state.web_config.cookie_secure,
        samesite="lax",
        max_age=result.max_age if dto.remember_me else None,
        path="/",
    )
    return LoginResponse(username=result.username)


@auth_router.get('/me')
async def me(request: Request, db: FromDishka[AsyncSession], sessions: FromDishka[RedisCache]) -> ProfileResponse:
    return ProfileResponse.model_validate(await current_user(request, db, sessions))


@auth_router.post('/logout', status_code=204)
async def logout(request: Request, sessions: FromDishka[RedisCache]) -> Response:
    session_id = request.cookies.get('session_id')
    if session_id:
        await sessions.delete_session(session_id)
    response = Response(status_code=204)
    response.delete_cookie('session_id', path='/')
    return response


class PasswordChange(BaseModel):
    model_config = ConfigDict(extra='forbid')
    current_password: Password
    new_password: Password


@auth_router.put('/password', status_code=204)
async def change_password(dto: PasswordChange, request: Request,
                          db: FromDishka[AsyncSession], sessions: FromDishka[RedisCache],
                          hasher: FromDishka[PasswordHasher]) -> Response:
    user = await current_user(request, db, sessions)
    user = await db.scalar(select(UserModel).where(UserModel.id == user.id)
                           .with_for_update().execution_options(populate_existing=True))
    try:
        if user.password_hash is None:
            raise HTTPException(400, 'Неверный текущий пароль')
        await run_in_threadpool(hasher.verify, user.password_hash, dto.current_password)
    except (VerificationError, InvalidHashError):
        raise HTTPException(400, 'Неверный текущий пароль')
    if dto.current_password == dto.new_password:
        raise HTTPException(422, 'Новый пароль должен отличаться от текущего')
    user.password_hash = await run_in_threadpool(hasher.hash, dto.new_password)
    user.last_password_change = datetime.now(timezone.utc)
    await db.commit()
    return Response(status_code=204)
