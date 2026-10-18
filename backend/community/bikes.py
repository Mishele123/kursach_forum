from datetime import datetime, timezone
from typing import Annotated
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request
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
