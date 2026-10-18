from typing import Annotated
from datetime import datetime
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from sqlalchemy.ext.asyncio import AsyncSession
from auth.current_user import current_user
from auth.repositories import RedisCache

Interest = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=80)]


class ProfileUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    city: Annotated[str, StringConstraints(strip_whitespace=True, max_length=100)] | None = None
    discipline: Annotated[str, StringConstraints(strip_whitespace=True, max_length=100)] | None = None
    interests: list[Interest] = Field(default_factory=list, max_length=20)
    bio: Annotated[str, StringConstraints(strip_whitespace=True, max_length=2000)] | None = None


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: str | None
    city: str | None
    discipline: str | None
    interests: list[str]
    bio: str | None
    created_at: datetime


router = APIRouter(prefix='/users', tags=['Profile'], route_class=DishkaRoute)


@router.get('/me')
async def get_profile(request: Request, db: FromDishka[AsyncSession], sessions: FromDishka[RedisCache]) -> ProfileResponse:
    return ProfileResponse.model_validate(await current_user(request, db, sessions))


@router.patch('/me')
async def update_profile(dto: ProfileUpdate, request: Request, db: FromDishka[AsyncSession],
                         sessions: FromDishka[RedisCache]) -> ProfileResponse:
    user = await current_user(request, db, sessions)
    for key, value in dto.model_dump(exclude_unset=True).items():
        setattr(user, key, value)
    await db.flush()
    result = ProfileResponse.model_validate(user)
    await db.commit()
    return result
