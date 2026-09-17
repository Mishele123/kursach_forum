from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Response, status

from auth.user_dto import CreateUserDto
from auth.user_interactor import CreateUserInteractor

router = APIRouter(tags=["auth"], route_class=DishkaRoute)


@router.post(path="/login")
async def create_user_route(
    dto: CreateUserDto, interactor: FromDishka[CreateUserInteractor], response: Response
):
    created_user: CreateUserDto = await interactor(dto)
    response.status_code = status.HTTP_201_CREATED
    return created_user
