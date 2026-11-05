from typing import Annotated
from datetime import datetime
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request, UploadFile, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from auth.services.auth_dto import Username
from auth.models import UserModel
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
    avatar_url: str | None = None
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


@router.put('/me/avatar')
async def upload_avatar(request: Request, file: UploadFile, db: FromDishka[AsyncSession],
                        sessions: FromDishka[RedisCache]) -> ProfileResponse:
    from community.media import receive_photo, remove_photo
    user = await current_user(request, db, sessions)
    # Refresh after acquiring the lock: concurrent uploads must replace the latest avatar.
    user = await db.scalar(select(UserModel).where(UserModel.id == user.id)
                           .with_for_update().execution_options(populate_existing=True))
    directory = request.app.state.upload_dir
    filename = await receive_photo(file, directory)
    previous = user.avatar_url
    try:
        user.avatar_url = f'/media/{filename}'
        result = ProfileResponse.model_validate(user)
        await db.commit()
    except BaseException:
        remove_photo(directory, filename)
        raise
    if previous and previous.startswith('/media/'):
        remove_photo(directory, previous.removeprefix('/media/'))
    return result


class UsernameUpdate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    username: Username


@router.patch('/me/username')
async def update_username(dto: UsernameUpdate, request: Request, db: FromDishka[AsyncSession],
                          sessions: FromDishka[RedisCache]) -> ProfileResponse:
    user = await current_user(request, db, sessions)
    user = await db.scalar(select(UserModel).where(UserModel.id == user.id)
                           .with_for_update().execution_options(populate_existing=True))
    user.username = dto.username
    try:
        # The database's case-insensitive unique constraint also handles races.
        await db.flush()
        result = ProfileResponse.model_validate(user)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(409, 'Имя пользователя уже занято')
    return result
