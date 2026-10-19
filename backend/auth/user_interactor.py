"""Business logic for user operations"""
from auth.user_dto import CreateUserDto
from auth.user_entity import User
from auth.user_interfaces import UserRepository
from auth.user_mapper import UserMapper


class CreateUserInteractor:
    """Handles user creation business logic (US1)"""
    
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    async def __call__(self, dto: CreateUserDto) -> User:
        """
        Create a new user from registration data.
        
        Args:
            dto: CreateUserDto with username and password
            
        Returns:
            Created User entity with assigned ID
            
        Raises:
            ValueError: If username already exists (TODO: implement check)
        """
        # TODO: Check if username already exists
        # existing_users = await self._repo.read_all()
        # if any(user.username == dto.username for user in existing_users):
        #     raise ValueError(f"Username '{dto.username}' already exists")
        
        # Convert DTO to Entity
        user = UserMapper.create_dto_to_entity(dto)
        
        # Persist to storage
        created_user = await self._repo.create(user)
        
        return created_user
