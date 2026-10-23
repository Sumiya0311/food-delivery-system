from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus, PaymentMethod, PaymentStatus


class OrderCreate(BaseModel):
    address_id: int = Field(gt=0)
    payment_method: PaymentMethod
    coupon_code: str | None = None
    tip: Decimal = Field(default=Decimal("0.00"), ge=0, le=1000)


class OrderItemResponse(BaseModel):
    id: int
    menu_item_id: int
    item_name: str
    unit_price: Decimal
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer_id: int
    restaurant_id: int
    address_id: int
    status: OrderStatus
    payment_method: PaymentMethod
    payment_status: PaymentStatus
    item_total: Decimal
    discount_amount: Decimal
    packaging_fee: Decimal
    delivery_fee: Decimal
    platform_fee: Decimal
    gst_amount: Decimal
    tip_amount: Decimal
    grand_total: Decimal
    created_at: datetime
    items: list[OrderItemResponse] = []

    model_config = ConfigDict(from_attributes=True)