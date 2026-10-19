from datetime import datetime

from pydantic import BaseModel, Field


class CreateBikeDto(BaseModel):
    """DTO for adding a bike (US5)"""
    brand: str = Field(..., min_length=1, max_length=100)
    model: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., ge=1800, le=2030)  # Year validation


class BikeResponseDto(BaseModel):
    """DTO for returning bike info"""
    id: int
    brand: str
    model: str
    year: int
    user_id: int
    created_at: datetime
