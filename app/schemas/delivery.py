from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LocationUpdate(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class AvailabilityUpdate(BaseModel):
    is_online: bool
    is_available: bool | None = None


class DeliveryPartnerResponse(BaseModel):
    id: int
    user_id: int
    vehicle_number: str
    vehicle_type: str
    is_online: bool
    is_available: bool
    latitude: float | None = None
    longitude: float | None = None

    model_config = ConfigDict(from_attributes=True)


class DeliveryOfferResponse(BaseModel):
    id: int
    order_id: int
    partner_id: int
    status: str
    offered_at: datetime
    expires_at: datetime
    responded_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class DeliveryOfferResponseUpdate(BaseModel):
    status: str = Field(pattern="^(Accepted|Rejected)$")