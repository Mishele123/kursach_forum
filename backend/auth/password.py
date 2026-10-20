"""Password hashing and verification utility using Argon2"""
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError


# Initialize Argon2 password hasher with secure defaults
_hasher = PasswordHasher(
    time_cost=2,  # Number of iterations
    memory_cost=65536,  # Memory usage in kB (64 MB)
    parallelism=1,  # Number of parallel threads
    hash_len=32,  # Length of the hash in bytes
    salt_len=16   # Length of random salt in bytes
)


def hash_password(plain_password: str) -> str:
    """
    Hash a plain text password using Argon2.
    
    Args:
        plain_password: The password to hash
        
    Returns:
        The hashed password string (includes salt and parameters)
        
    Example:
        >>> hashed = hash_password("mySecretPassword123")
        >>> print(hashed)
        $argon2id$v=19$m=65536,t=2,p=1$...
    """
    return _hasher.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    
    Args:
        plain_password: The password to verify
        hashed_password: The hashed password to check against
        
    Returns:
        True if password matches, False otherwise
        
    Example:
        >>> hashed = hash_password("myPassword")
        >>> verify_password("myPassword", hashed)
        True
        >>> verify_password("wrongPassword", hashed)
        False
    """
    try:
        _hasher.verify(hashed_password, plain_password)
        
        # Check if hash needs rehashing (parameters changed)
        if _hasher.check_needs_rehash(hashed_password):
            # In production, you might want to update the hash in database
            pass
            
        return True
    except VerifyMismatchError:
        return False


def needs_rehash(hashed_password: str) -> bool:
    """
    Check if a hashed password needs to be rehashed with updated parameters.
    
    Args:
        hashed_password: The hashed password to check
        
    Returns:
        True if password needs rehashing, False otherwise
    """
    return _hasher.check_needs_rehash(hashed_password)
