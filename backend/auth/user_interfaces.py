from abc import ABC, abstractmethod

from auth.user_entity import User


class UserRepository(ABC):
    @abstractmethod
    async def read_all(self) -> list[User]: ...

    @abstractmethod
    async def find_by_login(self, identity: str) -> User | None: ...

    @abstractmethod
    async def read(self, id: int) -> User | None: ...

    @abstractmethod
    async def create(self, entity: User) -> User: ...

    @abstractmethod
    async def update(self, entity: User) -> bool: ...

    @abstractmethod
    async def delete(self, id: int) -> bool: ...
