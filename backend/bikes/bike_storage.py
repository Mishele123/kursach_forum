from sqlalchemy import select

from database import Database
from models import BikeRow
from bikes.bike_entity import Bike


class BikeStorage:
    def __init__(self, database: Database):
        self.database = database

    async def create(self, entity: Bike) -> Bike:
        async with self.database.session() as session:
            row = BikeRow(**entity.model_dump(exclude={"id"}))
            session.add(row)
            await session.flush()
            entity.id = row.id
        return entity

    async def get_by_id(self, bike_id: int) -> Bike | None:
        async with self.database.session() as session:
            row = await session.get(BikeRow, bike_id)
            return Bike.model_validate(row, from_attributes=True) if row else None

    async def get_by_user(self, user_id: int) -> list[Bike]:
        async with self.database.session() as session:
            rows = (await session.scalars(select(BikeRow).where(BikeRow.user_id == user_id).order_by(BikeRow.id.desc()))).all()
            return [Bike.model_validate(row, from_attributes=True) for row in rows]
