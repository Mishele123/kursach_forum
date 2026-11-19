"""Role management: only administrators can grant or revoke moderator access."""
from typing import Annotated, Literal
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException, Path, Request
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from auth.current_user import current_user
from auth.models import UserModel, UserRole
from auth.repositories import RedisCache

router = APIRouter(prefix='/admin', tags=['Administration'], route_class=DishkaRoute)
UserId = Annotated[int, Path(ge=1, le=2147483647)]


class RoleChange(BaseModel):
    model_config = ConfigDict(extra='forbid')
    role: Literal['user', 'moderator']


class RoleResponse(BaseModel):
    id: int
    username: str
    role: str


@router.put('/users/{user_id}/role')
async def change_role(user_id: UserId, dto: RoleChange, request: Request,
                      db: FromDishka[AsyncSession], sessions: FromDishka[RedisCache]) -> RoleResponse:
    actor = await current_user(request, db, sessions)
    if actor.role != UserRole.ADMIN:
        raise HTTPException(403, 'Нужны права администратора')
    target = await db.scalar(select(UserModel).where(UserModel.id == user_id,
                              UserModel.deleted_at.is_(None)).with_for_update())
    if target is None:
        raise HTTPException(404, 'Пользователь не найден')
    if target.role == UserRole.ADMIN:
        raise HTTPException(403, 'Роль администратора нельзя менять через API')
    target.role = UserRole(dto.role)
    result = RoleResponse(id=target.id, username=target.username, role=target.role.value)
    await db.commit()
    return result
