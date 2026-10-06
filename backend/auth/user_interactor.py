from auth.user_dto import CreateUserDto, dto_to_user
from auth.user_entity import User
from auth.user_interfaces import UserRepository


class CreateUserInteractor:
    def __init__(self, repo: UserRepository):
        self._repo = repo

    async def __call__(self, dto: CreateUserDto) -> CreateUserDto:
        user_mapping: User = dto_to_user(dto)
        await self._repo.create(user_mapping)
        print(await self._repo.read_all())
        return dto
