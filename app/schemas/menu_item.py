from pydantic import BaseModel, ConfigDict, Field


class MenuItemCreate(BaseModel):
    restaurant_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=2, max_length=150)
    description: str | None = None
    category: str = Field(..., min_length=2, max_length=100)
    price: float = Field(..., gt=0)
    is_available: bool = True


class MenuItemResponse(BaseModel):
    id: int
    restaurant_id: int
    name: str
    description: str | None
    category: str
    price: float
    is_available: bool
    is_deleted: bool

    model_config = ConfigDict(from_attributes=True)