from datetime import datetime, timezone

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, HTTPException

from auth.user_interfaces import UserRepository
from bikes.bike_dto import CreateBikeDto, BikeResponseDto
from bikes.bike_entity import Bike
from bikes.bike_storage import BikeStorage

router = APIRouter(prefix="/bikes", tags=["bikes"], route_class=DishkaRoute)


@router.post("", status_code=201)
async def create_bike(
    dto: CreateBikeDto,
    bike_storage: FromDishka[BikeStorage],
    user_repo: FromDishka[UserRepository],
    user_id: int = 1  # Temporary: hardcoded (should come from JWT)
) -> BikeResponseDto:
    """Add a bike (US5)"""
    # Verify user exists
    user = await user_repo.read(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create bike
    bike = Bike(
        id=0,
        brand=dto.brand,
        model=dto.model,
        year=dto.year,
        user_id=user_id,
        created_at=datetime.now(timezone.utc)
    )
    
    created_bike = await bike_storage.create(bike)
    
    return BikeResponseDto(
        id=created_bike.id,
        brand=created_bike.brand,
        model=created_bike.model,
        year=created_bike.year,
        user_id=created_bike.user_id,
        created_at=created_bike.created_at
    )


@router.get("/my-bikes")
async def get_my_bikes(
    bike_storage: FromDishka[BikeStorage],
    user_id: int = 1  # Temporary: hardcoded
) -> list[BikeResponseDto]:
    """Get current user's bikes (US5)"""
    bikes = await bike_storage.get_by_user(user_id)
    
    return [
        BikeResponseDto(
            id=bike.id,
            brand=bike.brand,
            model=bike.model,
            year=bike.year,
            user_id=bike.user_id,
            created_at=bike.created_at
        )
        for bike in bikes
    ]
