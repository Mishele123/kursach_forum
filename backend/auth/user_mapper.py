"""User mapping utilities for converting between DTOs and Entities"""
from datetime import datetime, timezone

from auth.password import hash_password
from auth.user_dto import CreateUserDto, UpdateUserDto, UserResponseDto
from auth.user_entity import User, UserRole


class UserMapper:
    """Centralized user mapping logic following Single Responsibility Principle"""
    
    @staticmethod
    def create_dto_to_entity(dto: CreateUserDto) -> User:
        """
        Convert CreateUserDto to User Entity with default values.
        
        Args:
            dto: CreateUserDto containing username and password
            
        Returns:
            User entity ready to be persisted
            
        Note:
            - ID will be set by storage layer
            - Password is hashed using Argon2
            - All optional fields initialized with None or default values
        """
        now = datetime.now(timezone.utc)
        
        return User(
            id=0,  # Will be assigned by storage
            username=dto.username.strip(),
            password_hash=hash_password(dto.password),  # Hash password with Argon2
            email=dto.email,
            role=UserRole.USER,
            avatar_url=None,
            bio=None,
            is_banned=False,
            created_at=now,
            updated_at=now,
            last_login_at=None,
            email_verified_at=None,
            last_password_change=now,
            city=None,
            discipline=None,
            interests=None,
        )
    
    @staticmethod
    def entity_to_response_dto(user: User) -> UserResponseDto:
        """
        Convert User Entity to UserResponseDto (safe for client exposure).
        
        Args:
            user: User entity from storage
            
        Returns:
            UserResponseDto without sensitive fields (password_hash, is_banned, etc.)
            
        Security:
            Excludes: password_hash, is_banned, last_login_at, last_password_change
        """
        return UserResponseDto(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role,
            avatar_url=user.avatar_url,
            bio=user.bio,
            city=user.city,
            discipline=user.discipline,
            interests=user.interests,
            created_at=user.created_at
        )
    
    @staticmethod
    def entity_list_to_response_dto_list(users: list[User]) -> list[UserResponseDto]:
        """
        Batch convert User entities to UserResponseDTOs.
        
        Args:
            users: List of User entities
            
        Returns:
            List of UserResponseDTOs
        """
        return [UserMapper.entity_to_response_dto(user) for user in users]
    
    @staticmethod
    def update_entity_from_dto(user: User, dto: UpdateUserDto) -> User:
        """
        Apply UpdateUserDto changes to existing User entity.
        
        Args:
            user: Existing User entity to update
            dto: UpdateUserDto with new values (None values are ignored)
            
        Returns:
            Updated User entity
            
        Note:
            Only updates fields that are not None in the DTO (partial update pattern)
        """
        if dto.city is not None:
            user.city = dto.city
        
        if dto.discipline is not None:
            user.discipline = dto.discipline
        
        if dto.interests is not None:
            user.interests = dto.interests
        
        if dto.bio is not None:
            user.bio = dto.bio
        
        # Update timestamp
        user.updated_at = datetime.now(timezone.utc)
        
        return user
