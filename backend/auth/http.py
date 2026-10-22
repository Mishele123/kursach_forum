from starlette.concurrency import run_in_threadpool
"""HTTP endpoints for user authentication and profile management"""
from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status, HTTPException, Response, Request
import os
from datetime import datetime, timezone

from auth.dependencies import CurrentUserId
from auth.session import SESSION_SECONDS
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
    description="Authenticate user with username and password, returns session token (US1)"
)
async def login_user(
    dto: LoginDto,
    response: Response,
    request: Request,
    repo: FromDishka[UserRepository]
) -> dict:
    """
    Login with username and password.

    - **username**: Your username
    - **password**: Your password

    Returns session access token and user info.
    """
    user = await repo.find_by_login(dto.email or dto.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Verify password using Argon2
    if not await run_in_threadpool(verify_password, dto.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    if user.is_banned:
        raise HTTPException(403, "User account is banned")

    user.last_login_at = datetime.now(timezone.utc)
    await repo.update(user)

    # Create login session
    access_token = await request.app.state.sessions.create_access_token(user.id)

    response.set_cookie("velo_session", access_token, httponly=True, secure=os.environ.get("VELO_COOKIE_SECURE") == "1", samesite="lax", max_age=SESSION_SECONDS)

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
async def get_current_user_profile(
    user_id: CurrentUserId,
    repo: FromDishka[UserRepository]
) -> UserResponseDto:
    """
    Get current user's profile.

    Requires: Bearer token in Authorization header
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
    user_id: CurrentUserId,
    repo: FromDishka[UserRepository]
) -> UserResponseDto:
    """
    Update current user's profile (partial update).

    Only provided fields will be updated. Null/None values are ignored.

    Requires: Bearer token in Authorization header
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


@router.post("/logout", status_code=204)
async def logout(request: Request, response: Response):
    tokens = [request.cookies.get("velo_session", ""), request.headers.get("authorization", "").removeprefix("Bearer ")]
    for token in tokens:
        if token:
            await request.app.state.sessions.revoke_token(token)
    response.delete_cookie("velo_session")
