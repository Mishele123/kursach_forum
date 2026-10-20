"""FastAPI dependencies for authentication and authorization"""
from typing import Annotated

from dishka.integrations.fastapi import FromDishka
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from auth.jwt import verify_token, TokenData
from auth.user_entity import User
from auth.user_interfaces import UserRepository


# OAuth2 Bearer token scheme (Authorization: Bearer <token>)
security = HTTPBearer()


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> int:
    """
    Extract and verify JWT token, return user_id.
    
    This is a lightweight dependency that only returns the user_id.
    Use this when you only need to identify the user without loading full data.
    
    Args:
        credentials: HTTP Authorization header with Bearer token
        
    Returns:
        user_id extracted from valid JWT token
        
    Raises:
        HTTPException 401: If token is missing, invalid, or expired
        
    Example:
        ```python
        @router.get("/my-posts")
        async def my_posts(user_id: Annotated[int, Depends(get_current_user_id)]):
            return await get_posts_by_user(user_id)
        ```
    """
    token = credentials.credentials
    
    # Verify and decode token
    token_data = verify_token(token)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_data.user_id


async def get_current_user(
    user_id: Annotated[int, Depends(get_current_user_id)],
    repo: FromDishka[UserRepository]
) -> User:
    """
    Get the current authenticated user's full entity.
    
    This dependency loads the complete User entity from database.
    Use this when you need access to user's profile, role, etc.
    
    Args:
        user_id: User ID from JWT token (injected by get_current_user_id)
        repo: UserRepository (injected by Dishka)
        
    Returns:
        Full User entity from database
        
    Raises:
        HTTPException 401: If token is invalid
        HTTPException 404: If user not found in database
        
    Example:
        ```python
        @router.get("/profile")
        async def get_profile(current_user: Annotated[User, Depends(get_current_user)]):
            return {"username": current_user.username, "bio": current_user.bio}
        ```
    """
    user = await repo.read(user_id)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    if user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is banned"
        )
    
    return user


async def get_token_data(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> TokenData:
    """
    Extract and return full token data without loading user from DB.
    
    Use this when you need both user_id and username from token
    without making a database query.
    
    Args:
        credentials: HTTP Authorization header with Bearer token
        
    Returns:
        TokenData with user_id and username
        
    Raises:
        HTTPException 401: If token is invalid or expired
    """
    token = credentials.credentials
    token_data = verify_token(token)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token_data


# Type aliases for cleaner endpoint signatures
CurrentUserId = Annotated[int, Depends(get_current_user_id)]
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentTokenData = Annotated[TokenData, Depends(get_token_data)]
