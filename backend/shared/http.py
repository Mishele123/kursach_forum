"""Shared HTTP endpoints for file uploads and other utilities"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pydantic import BaseModel

from auth.dependencies import CurrentUserId
from shared.upload import save_upload_file, MAX_FILE_SIZE, ALLOWED_EXTENSIONS


router = APIRouter(tags=["uploads"])


class UploadResponse(BaseModel):
    """Response model for file upload"""
    filename: str
    file_path: str
    url: str
    size_bytes: int


@router.post(
    "/uploads",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a file",
    description="Upload an image file for posts or profile (US3 - photo upload)"
)
async def upload_file(
    user_id: CurrentUserId,
    file: UploadFile = File(..., description="Image file to upload")
) -> UploadResponse:
    """
    Upload an image file.
    
    Requires: Bearer token in Authorization header
    
    **Validation:**
    - Max file size: 5 MB
    - Allowed formats: JPG, JPEG, PNG, GIF, WEBP
    - Content-Type validation
    
    **Returns:**
    - filename: Original filename
    - file_path: Server path to file
    - url: Public URL to access the file
    - size_bytes: File size in bytes
    
    **Example:**
    ```bash
    curl -X POST "http://localhost:8000/uploads" \\
      -H "Authorization: Bearer your_token_here" \\
      -F "file=@photo.jpg"
    ```
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required"
        )
    
    # Get file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    # Save file (includes validation)
    file_path = await save_upload_file(file, user_id=user_id)
    
    # Generate public URL
    file_url = "/" + file_path
    
    return UploadResponse(
        filename=file.filename,
        file_path=file_path,
        url=file_url,
        size_bytes=file_size
    )


@router.get(
    "/uploads/info",
    summary="Get upload configuration",
    description="Get information about upload limits and allowed file types"
)
async def get_upload_info() -> dict:
    """
    Get upload configuration and limits.
    
    Returns information about:
    - Maximum file size
    - Allowed file extensions
    - Allowed MIME types
    """
    return {
        "max_file_size_bytes": MAX_FILE_SIZE,
        "max_file_size_mb": MAX_FILE_SIZE / 1024 / 1024,
        "allowed_extensions": list(ALLOWED_EXTENSIONS),
        "allowed_mime_types": [
            "image/jpeg",
            "image/png",
            "image/gif",
            "image/webp"
        ]
    }
