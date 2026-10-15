from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, Request, Response, status

from sqlalchemy.ext.asyncio import AsyncSession
from auth.current_user import current_user
from auth.repositories import RedisCache
from community.profile import ProfileResponse
from pydantic import BaseModel

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
