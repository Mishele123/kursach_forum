from datetime import datetime

from pydantic import BaseModel


class Bike(BaseModel):
    """Bike model for Sprint 1 - US5"""
    id: int
    brand: str  # Бренд
    model: str  # Модель
    year: int  # Год выпуска
    user_id: int  # Owner
    created_at: datetime
