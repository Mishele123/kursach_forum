"""User domain models and entities"""
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class UserRole(StrEnum):
    """User roles for authorization"""
    USER = "USER"
    MODERATOR = "MODERATOR"
    ADMIN = "ADMIN"


class User(BaseModel):
    """
    User entity representing a registered user in the system.
    
    This is the core domain model containing all user information.
    Used internally by the application - never exposed directly to clients.
    """
    id: int = Field(..., description="Unique user identifier")
    email: str | None = Field(None, description="Email address (unique, optional)")
    username: str = Field(..., description="Username for login (unique, required)")
    password_hash: str = Field(..., description="Hashed password (never plain text)")
    role: UserRole = Field(default=UserRole.USER, description="User role for permissions")
    avatar_url: str | None = Field(None, description="URL to user's avatar image")
    bio: str | None = Field(None, description="User biography/description")
    is_banned: bool = Field(default=False, description="Whether user is banned")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last profile update timestamp")
    last_login_at: datetime | None = Field(None, description="Last successful login timestamp")
    email_verified_at: datetime | None = Field(None, description="Email verification timestamp")
    last_password_change: datetime = Field(..., description="Last password change (for session invalidation)")
    
    # Sprint 1 profile fields (US2)
    city: str | None = Field(None, description="City of residence")
    discipline: str | None = Field(None, description="Cycling discipline (MTB, Road, Gravel, etc.)")
    interests: str | None = Field(None, description="Cycling interests and preferences")
