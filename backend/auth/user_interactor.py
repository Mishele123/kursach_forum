from starlette.concurrency import run_in_threadpool
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
            HTTPException 409: If username or email already exists
        """
        # Convert DTO to Entity
        user = await run_in_threadpool(UserMapper.create_dto_to_entity, dto)
        
        # Persist to storage
        created_user = await self._repo.create(user)
        
        return created_user
