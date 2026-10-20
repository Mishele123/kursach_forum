"""HTTP endpoints for user authentication and profile management"""
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status, HTTPException

from auth.dependencies import CurrentUser, CurrentUserId
from auth.jwt import create_access_token
from auth.password import verify_password
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
    description="Authenticate user with username and password, returns JWT token (US1)"
)
async def login_user(
    dto: LoginDto,
    repo: FromDishka[UserRepository]
) -> dict:
    """
    Login with username and password.
    
    - **username**: Your username
    - **password**: Your password
    
    Returns JWT access token and user info.
    """
    # Find user by username
    all_users = await repo.read_all()
    user = next((u for u in all_users if u.username == dto.username), None)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Verify password using Argon2
    if not verify_password(dto.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Create JWT access token
    access_token = create_access_token(user_id=user.id, username=user.username)
    
    # Return token and user info
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserMapper.entity_to_response_dto(user)
    }


@router.get(
    path="/me",
    response_model=UserResponseDto,
    summary="Get current user profile",
    description="Retrieve current authenticated user's profile information (US2)"
)
async def get_current_user(
    current_user: CurrentUser
) -> UserResponseDto:
    """
    Get current user's profile.
    
    Requires: Bearer token in Authorization header
    """
    return UserMapper.entity_to_response_dto(current_user)


@router.put(
    path="/me",
    response_model=UserResponseDto,
    summary="Update user profile",
    description="Update current user's profile information (US2)"
)
async def update_profile(
    dto: UpdateUserDto,
    current_user: CurrentUser,
    repo: FromDishka[UserRepository]
) -> UserResponseDto:
    """
    Update current user's profile (partial update).
    
    Only provided fields will be updated. Null/None values are ignored.
    
    Requires: Bearer token in Authorization header
    """
    # Apply updates from DTO to current user entity
    updated_user = UserMapper.update_entity_from_dto(current_user, dto)
    
    # Persist changes
    await repo.update(updated_user)
    
    # Return updated user info
    return UserMapper.entity_to_response_dto(updated_user)
