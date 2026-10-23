from pydantic import BaseModel, ConfigDict, Field


class AddressCreate(BaseModel):
    label: str = Field(..., min_length=2, max_length=50)
    recipient_name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., pattern=r"^[0-9]{10}$")
    address_line: str = Field(..., min_length=5, max_length=255)
    city: str = Field(..., min_length=2, max_length=100)
    pincode: str = Field(..., pattern=r"^[0-9]{6}$")
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    is_default: bool = False


class AddressResponse(BaseModel):
    id: int
    user_id: int
    label: str
    recipient_name: str
    phone: str
    address_line: str
    city: str
    pincode: str
    latitude: float
    longitude: float
    is_default: bool

    model_config = ConfigDict(from_attributes=True)