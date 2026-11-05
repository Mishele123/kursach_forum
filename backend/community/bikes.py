from datetime import datetime, timezone
from typing import Annotated
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request, UploadFile, HTTPException, Path
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from auth.current_user import current_user
from auth.repositories import RedisCache
from community.models import Bike

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


class BikeCreate(BaseModel):
    model_config = ConfigDict(extra='forbid')
    brand: Name
    model: Name
    year: int = Field(ge=1800, le=2200, strict=True)

    @field_validator('year')
    @classmethod
    def check_year(cls, value):
        if value > datetime.now(timezone.utc).year + 1:
            raise ValueError('Год не может быть позднее следующего календарного года')
        return value


class BikeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    brand: str
    model: str
    year: int
    photo_url: str | None


router = APIRouter(prefix='/users/me/bikes', tags=['Bikes'], route_class=DishkaRoute)


@router.post('', status_code=201)
async def add_bike(dto: BikeCreate, request: Request, db: FromDishka[AsyncSession],
                   sessions: FromDishka[RedisCache]) -> BikeResponse:
    user = await current_user(request, db, sessions)
    bike = Bike(owner_id=user.id, **dto.model_dump())
    db.add(bike)
    await db.flush()
    result = BikeResponse.model_validate(bike)
    await db.commit()
    return result


@router.get('')
async def my_bikes(request: Request, db: FromDishka[AsyncSession], sessions: FromDishka[RedisCache]) -> list[BikeResponse]:
    user = await current_user(request, db, sessions)
    bikes = await db.scalars(select(Bike).where(Bike.owner_id == user.id).order_by(Bike.id))
    return [BikeResponse.model_validate(bike) for bike in bikes]


@router.put('/{bike_id}/photo')
async def upload_bike_photo(bike_id: Annotated[int, Path(ge=1, le=2147483647)],
                            request: Request, file: UploadFile,
                            db: FromDishka[AsyncSession], sessions: FromDishka[RedisCache]) -> BikeResponse:
    from community.media import receive_photo, remove_photo
    user = await current_user(request, db, sessions)
    bike = await db.scalar(select(Bike).where(Bike.id == bike_id).with_for_update())
    if bike is None:
        raise HTTPException(404, 'Велосипед не найден')
    if bike.owner_id != user.id:
        raise HTTPException(403, 'Изменять фотографию может только владелец')
    directory = request.app.state.upload_dir
    filename = await receive_photo(file, directory)
    previous = bike.photo_filename
    try:
        bike.photo_filename = filename
        result = BikeResponse.model_validate(bike)
        await db.commit()
    except BaseException:
        remove_photo(directory, filename)
        raise
    remove_photo(directory, previous)
    return result
