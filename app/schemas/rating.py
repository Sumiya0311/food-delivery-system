from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RatingCreate(BaseModel):
    order_id: int = Field(gt=0)
    rating: int = Field(ge=1, le=5)
    review: str | None = Field(default=None, max_length=2000)


class RatingResponse(BaseModel):
    id: int
    order_id: int
    customer_id: int
    restaurant_id: int
    rating: int
    review: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)