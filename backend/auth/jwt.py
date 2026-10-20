"""JWT token creation and verification utilities"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from pydantic import BaseModel


# Secret key for JWT encoding/decoding
# In production, this MUST be stored in environment variables!
SECRET_KEY = "your-secret-key-change-this-in-production-use-env-variable-minimum-32-chars"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


class TokenData(BaseModel):
    """Data structure for JWT token payload"""
    user_id: int
    username: str


def create_access_token(user_id: int, username: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        user_id: The user's ID
        username: The user's username
        expires_delta: Optional expiration time delta (defaults to 7 days)
        
    Returns:
        Encoded JWT token string
        
    Example:
        >>> token = create_access_token(user_id=1, username="john_doe")
        >>> print(token)
        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    """
    to_encode = {
        "sub": str(user_id),  # Subject (user_id)
        "username": username,
        "iat": datetime.now(timezone.utc),  # Issued at
    }
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode["exp"] = expire  # Expiration time
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[TokenData]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: The JWT token to verify
        
    Returns:
        TokenData if valid, None if invalid or expired
        
    Example:
        >>> token = create_access_token(1, "john_doe")
        >>> token_data = verify_token(token)
        >>> print(token_data.user_id, token_data.username)
        1 john_doe
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        
        if user_id is None or username is None:
            return None
            
        return TokenData(user_id=int(user_id), username=username)
    except JWTError:
        return None
    except (ValueError, KeyError):
        return None


def decode_token(token: str) -> dict:
    """
    Decode a JWT token without verification (for debugging).
    
    Args:
        token: The JWT token to decode
        
    Returns:
        Decoded payload dictionary
        
    Note:
        This does NOT verify the token! Use verify_token() in production.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        return {"error": str(e)}
