"""File upload utilities and validation"""
import os
import uuid
import io
import warnings
from PIL import Image, UnidentifiedImageError
from starlette.concurrency import run_in_threadpool
from pathlib import Path
from typing import Optional

from fastapi import UploadFile, HTTPException, status


# Configuration
UPLOAD_DIR = Path(os.environ.get("VELO_UPLOAD_DIR", str(Path(__file__).resolve().parents[2] / "uploads")))
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
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
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


async def save_upload_file(file: UploadFile, upload_dir: Path = UPLOAD_DIR, user_id: int = 0) -> str:
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
    unique_filename = f"{user_id}_" + generate_unique_filename(file.filename or "upload.jpg")
    file_path = upload_dir / unique_filename
    
    # Save file
    try:
        contents = await file.read(MAX_FILE_SIZE + 1)
        if not contents:
            raise HTTPException(400, "Empty image file")
        ext = Path(file.filename or "").suffix.lower()
        expected_mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp"}
        if file.content_type != expected_mime.get(ext):
            raise HTTPException(400, "Image extension and MIME type must match")
        signatures = {
            ".jpg": contents.startswith(b"\xff\xd8\xff"),
            ".jpeg": contents.startswith(b"\xff\xd8\xff"),
            ".png": contents.startswith(b"\x89PNG\r\n\x1a\n"),
            ".gif": contents.startswith((b"GIF87a", b"GIF89a")),
            ".webp": contents.startswith(b"RIFF") and contents[8:12] == b"WEBP",
        }
        if not signatures.get(ext):
            raise HTTPException(400, "File contents do not match the image format")
        def validate_and_save():
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("error", Image.DecompressionBombWarning)
                    with Image.open(io.BytesIO(contents)) as image:
                        if image.format not in {"JPEG", "PNG", "GIF", "WEBP"}:
                            raise ValueError("Unsupported image")
                        image.verify()
            except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
                raise HTTPException(400, "Файл повреждён или не является допустимым изображением") from error
            file_path.write_bytes(contents)
        await run_in_threadpool(validate_and_save)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    finally:
        await file.close()
    
    # Return relative path for storage in database
    return f"uploads/{unique_filename}"
