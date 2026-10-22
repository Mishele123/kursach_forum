"""Data Transfer Objects for User operations"""
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, field_validator
import re

from auth.user_entity import UserRole


class CreateUserDto(BaseModel):
    email: str = Field(..., max_length=254)

    @field_validator("username")
    @classmethod
    def valid_username(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 3:
            raise ValueError("Username must contain at least 3 characters")
        return value

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", value):
            raise ValueError("Enter a valid email address")
        return value

    """DTO for user registration (US1)"""
    username: str = Field(..., min_length=3, max_length=50, description="Username for login")
    password: str = Field(..., min_length=6, max_length=256, description="Password (will be hashed)")
    
    model_config = ConfigDict(json_schema_extra={
            "example": {
                "username": "john_doe",
                "password": "mySecretPassword"
            }
        })


class UpdateUserDto(BaseModel):
    """DTO for updating user profile (US2)"""
    city: str | None = Field(None, max_length=100, description="City of residence")
    discipline: str | None = Field(None, max_length=100, description="Cycling discipline (MTB, Road, etc.)")
    interests: str | None = Field(None, max_length=500, description="Cycling interests")
    bio: str | None = Field(None, max_length=1000, description="User biography")
    
    model_config = ConfigDict(json_schema_extra={
            "example": {
                "city": "Moscow",
                "discipline": "MTB",
                "interests": "Trail riding, bike parks",
                "bio": "Passionate mountain biker"
            }
        })


class LoginDto(BaseModel):
    email: str | None = Field(None, max_length=254)
    """DTO for user login (US1)"""
    username: str = Field(default="", max_length=254, description="Username or email")
    password: str = Field(..., min_length=1, max_length=256, description="Password")
    
    model_config = ConfigDict(json_schema_extra={
            "example": {
                "username": "john_doe",
                "password": "mySecretPassword"
            }
        })


class UserResponseDto(BaseModel):
    """DTO for returning user info (without sensitive data)"""
    id: int = Field(..., description="Unique user ID")
    username: str = Field(..., description="Username")
    email: str | None = Field(None, description="User email")
    role: UserRole = Field(..., description="User role (USER, MODERATOR, ADMIN)")
    avatar_url: str | None = Field(None, description="Avatar image URL")
    bio: str | None = Field(None, description="User biography")
    city: str | None = Field(None, description="City of residence")
    discipline: str | None = Field(None, description="Cycling discipline")
    interests: str | None = Field(None, description="Cycling interests")
    created_at: datetime = Field(..., description="Account creation timestamp")
    
    model_config = ConfigDict(json_schema_extra={
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "role": "USER",
                "avatar_url": "https://example.com/avatar.jpg",
                "bio": "Passionate cyclist",
                "city": "Moscow",
                "discipline": "MTB",
                "interests": "Trail riding",
                "created_at": "2024-01-15T10:30:00Z"
            }
        })
