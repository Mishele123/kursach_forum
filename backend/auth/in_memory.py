from auth.seed import UserSeed
from auth.user_entity import User
from auth.user_interfaces import UserRepository


class MemoryStorage(UserRepository):
    def __init__(self) -> None:
        self.seed = UserSeed()()

    async def read_all(self) -> list[User]:
        return self.seed

    async def read(self, id: int) -> User | None:
        for usr in self.seed:
            if usr.id == id:
                return usr
        return None

    async def create(self, entity: User) -> User:
        if entity.id == 0:
            entity.id = (
                max(self.seed, key=lambda usr: usr.id).id + 1
                if len(self.seed) > 0
                else 1
            )
        self.seed.append(entity)
        return entity

    async def update(self, entity: User) -> bool:
        for idx, usr in enumerate(self.seed):
            if usr.id == entity.id:
                self.seed[idx] = entity
                return True
        return False

    async def delete(self, id: int) -> bool:
        for idx, usr in enumerate(self.seed):
            if usr.id == id:
                self.seed.pop(idx)
                return True
        return False
