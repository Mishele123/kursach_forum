"""File upload utilities and validation"""
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import UploadFile, HTTPException, status


# Configuration
UPLOAD_DIR = Path("uploads")
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB in bytes
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png", 
    "image/gif",
    "image/webp"
}


def validate_file_size(file: UploadFile, max_size: int = MAX_FILE_SIZE) -> None:
    """
    Validate file size.
    
    Args:
        file: The uploaded file
        max_size: Maximum allowed size in bytes
        
    Raises:
        HTTPException 413: If file exceeds max size
    """
    # Read file to check size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()  # Get position (file size)
    file.file.seek(0)  # Reset to beginning
    
    if file_size > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size {file_size / 1024 / 1024:.2f}MB exceeds maximum allowed size {max_size / 1024 / 1024:.0f}MB"
        )


def validate_file_extension(filename: str, allowed_extensions: set[str] = ALLOWED_EXTENSIONS) -> None:
    """
    Validate file extension.
    
    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed extensions (with dots, e.g., {".jpg", ".png"})
        
    Raises:
        HTTPException 400: If extension not allowed
    """
    ext = Path(filename).suffix.lower()
    
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension '{ext}' not allowed. Allowed: {', '.join(allowed_extensions)}"
        )


def validate_content_type(content_type: Optional[str], allowed_types: set[str] = ALLOWED_CONTENT_TYPES) -> None:
    """
    Validate file content type (MIME type).
    
    Args:
        content_type: Content-Type header from upload
        allowed_types: Set of allowed MIME types
        
    Raises:
        HTTPException 400: If content type not allowed
    """
    if not content_type or content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Content type '{content_type}' not allowed. Allowed: {', '.join(allowed_types)}"
        )


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a unique filename to prevent collisions.
    
    Args:
        original_filename: Original name of the uploaded file
        
    Returns:
        Unique filename with UUID prefix and original extension
        
    Example:
        >>> generate_unique_filename("photo.jpg")
        '550e8400-e29b-41d4-a716-446655440000.jpg'
    """
    ext = Path(original_filename).suffix.lower()
    unique_id = uuid.uuid4()
    return f"{unique_id}{ext}"


async def save_upload_file(file: UploadFile, upload_dir: Path = UPLOAD_DIR) -> str:
    """
    Save uploaded file to disk and return its path.
    
    Args:
        file: The uploaded file from FastAPI
        upload_dir: Directory to save files (created if doesn't exist)
        
    Returns:
        Relative path to saved file (e.g., "uploads/uuid.jpg")
        
    Raises:
        HTTPException: If validation fails or save error occurs
    """
    # Validate
    validate_file_size(file)
    validate_file_extension(file.filename or "")
    validate_content_type(file.content_type)
    
    # Create upload directory if doesn't exist
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique filename
    unique_filename = generate_unique_filename(file.filename or "upload.jpg")
    file_path = upload_dir / unique_filename
    
    # Save file
    try:
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    finally:
        await file.close()
    
    # Return relative path for storage in database
    return str(file_path)


def delete_file(file_path: str) -> bool:
    """
    Delete a file from disk.
    
    Args:
        file_path: Path to the file to delete
        
    Returns:
        True if deleted, False if file doesn't exist
    """
    try:
        Path(file_path).unlink(missing_ok=True)
        return True
    except Exception:
        return False


def get_file_url(file_path: str, base_url: str = "http://localhost:8000") -> str:
    """
    Convert file path to public URL.
    
    Args:
        file_path: Relative file path (e.g., "uploads/uuid.jpg")
        base_url: Base URL of the API
        
    Returns:
        Full URL to access the file
        
    Example:
        >>> get_file_url("uploads/abc123.jpg")
        'http://localhost:8000/uploads/abc123.jpg'
    """
    # Normalize path separators to forward slashes for URLs
    normalized_path = file_path.replace("\\", "/")
    return f"{base_url}/{normalized_path}"
