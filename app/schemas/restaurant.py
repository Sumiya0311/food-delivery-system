from datetime import time

from pydantic import BaseModel, ConfigDict, Field


class RestaurantCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: str | None = None
    address: str = Field(..., min_length=5, max_length=255)

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

    delivery_radius_km: float = Field(default=5.0, gt=0, le=100)

    opening_time: time
    closing_time: time

    estimated_prep_minutes: int = Field(default=30, ge=5, le=240)


class RestaurantResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    description: str | None
    address: str
    latitude: float
    longitude: float
    delivery_radius_km: float
    opening_time: time
    closing_time: time
    is_open: bool
    is_active: bool
    average_rating: float
    estimated_prep_minutes: int

    model_config = ConfigDict(from_attributes=True)