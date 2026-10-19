from bikes.bike_entity import Bike


class BikeStorage:
    """In-memory storage for bikes"""
    
    def __init__(self):
        self.bikes: list[Bike] = []
        self._next_id = 1
    
    async def create(self, bike: Bike) -> Bike:
        """Create a new bike"""
        if bike.id == 0:
            bike.id = self._next_id
            self._next_id += 1
        self.bikes.append(bike)
        return bike
    
    async def get_by_user(self, user_id: int) -> list[Bike]:
        """Get all bikes for a user (US5)"""
        return [b for b in self.bikes if b.user_id == user_id]
    
    async def get_by_id(self, bike_id: int) -> Bike | None:
        """Get bike by ID"""
        for bike in self.bikes:
            if bike.id == bike_id:
                return bike
        return None
