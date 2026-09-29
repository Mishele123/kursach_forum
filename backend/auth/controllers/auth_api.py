from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, Request, Response, status

from auth.services import (
    CreateUserInteractor,
    LoginUserInteractor,
    UserRequestCreateDto,
    UserRequestLoginDto,
    UserResponceCreateDto,
    UserResponceLoginDto,
)

auth_router = APIRouter(prefix="/auth", route_class=DishkaRoute)


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    dto: UserRequestCreateDto, interactor: FromDishka[CreateUserInteractor]
) -> UserResponceCreateDto:
    return await interactor(dto)


@auth_router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    dto: UserRequestLoginDto,
    request: Request,
    response: Response,
    interactor: FromDishka[LoginUserInteractor],
) -> UserResponceLoginDto:

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
        secure=False,
        samesite="lax",
        max_age=result.max_age if dto.remember_me else None,
        path="/",
    )
    return result
