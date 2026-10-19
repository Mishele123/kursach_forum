"""HTTP endpoints for user authentication and profile management"""
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status, HTTPException

from auth.user_dto import CreateUserDto, LoginDto, UserResponseDto, UpdateUserDto
from auth.user_interactor import CreateUserInteractor
from auth.user_interfaces import UserRepository
from auth.user_mapper import UserMapper

router = APIRouter(tags=["auth"], route_class=DishkaRoute)


@router.post(
    path="/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponseDto,
    summary="Register new user",
    description="Create a new user account with username and password (US1)"
)
async def register_user(
    dto: CreateUserDto,
    interactor: FromDishka[CreateUserInteractor]
) -> UserResponseDto:
    """
    Register a new user account.
    
    - **username**: Unique username (min 3 chars)
    - **password**: Password (min 6 chars, will be hashed)
    
    Returns user info without password.
    """
    # Create user via interactor (handles business logic)
    created_user = await interactor(dto)
    
    # Convert Entity to safe ResponseDTO
    return UserMapper.entity_to_response_dto(created_user)


@router.post(
    path="/login",
    response_model=dict,
    summary="User login",
    description="Authenticate user with username and password (US1)"
)
async def login_user(
    dto: LoginDto,
    repo: FromDishka[UserRepository]
) -> dict:
    """
    Login with username and password.
    
    - **username**: Your username
    - **password**: Your password
    
    Returns user info (TODO: should return JWT token).
    """
    # Find user by username
    all_users = await repo.read_all()
    user = next((u for u in all_users if u.username == dto.username), None)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Verify password (TODO: use proper password hashing verification)
    if user.password_hash != dto.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Return success with user info (TODO: return JWT token instead)
    return {
        "message": "Login successful",
        "user": UserMapper.entity_to_response_dto(user)
    }


@router.get(
    path="/me",
    response_model=UserResponseDto,
    summary="Get current user profile",
    description="Retrieve current authenticated user's profile information (US2)"
)
async def get_current_user(
    repo: FromDishka[UserRepository],
    user_id: int = 1  # TODO: Extract from JWT token instead of hardcoded
) -> UserResponseDto:
    """
    Get current user's profile.
    
    TODO: user_id should come from JWT token authentication.
    """
    user = await repo.read(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    return UserMapper.entity_to_response_dto(user)


@router.put(
    path="/me",
    response_model=UserResponseDto,
    summary="Update user profile",
    description="Update current user's profile information (US2)"
)
async def update_profile(
    dto: UpdateUserDto,
    repo: FromDishka[UserRepository],
    user_id: int = 1  # TODO: Extract from JWT token instead of hardcoded
) -> UserResponseDto:
    """
    Update current user's profile (partial update).
    
    Only provided fields will be updated. Null/None values are ignored.
    
    TODO: user_id should come from JWT token authentication.
    """
    # Retrieve existing user
    user = await repo.read(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Apply updates from DTO
    updated_user = UserMapper.update_entity_from_dto(user, dto)
    
    # Persist changes
    await repo.update(updated_user)
    
    # Return updated user info
    return UserMapper.entity_to_response_dto(updated_user)
