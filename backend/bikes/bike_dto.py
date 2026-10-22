from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class CreateBikeDto(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    """DTO for adding a bike (US5)"""
    brand: str = Field(..., min_length=1, max_length=100)
    model: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., ge=1800, le=datetime.now().year + 1)  # Year validation
    photo_url: str | None = Field(None, max_length=255)


class BikeResponseDto(BaseModel):
    """DTO for returning bike info"""
    id: int
    brand: str
    model: str
    year: int
    user_id: int
    created_at: datetime
    photo_url: str | None = None
