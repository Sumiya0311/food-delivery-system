from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.order_item import OrderItem
import enum
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base, TimestampMixin


class OrderStatus(str, enum.Enum):
    PLACED = "Placed"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
    PREPARING = "Preparing"
    READY = "Ready"
    ASSIGNED = "Assigned"
    PICKED_UP = "Picked Up"
    OUT_FOR_DELIVERY = "Out for Delivery"
    DELIVERED = "Delivered"
    CANCELLED = "Cancelled"


class PaymentMethod(str, enum.Enum):
    ONLINE = "Online"
    COD = "COD"


class PaymentStatus(str, enum.Enum):
    PENDING = "Pending"
    PAID = "Paid"
    REFUNDED = "Refunded"


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_number: Mapped[str] = mapped_column(
        String(30), unique=True, index=True, nullable=False
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id"), nullable=False, index=True
    )
    address_id: Mapped[int] = mapped_column(
        ForeignKey("addresses.id"), nullable=False
    )
    coupon_id: Mapped[int | None] = mapped_column(
        ForeignKey("coupons.id"), nullable=True
    )

    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status"),
        default=OrderStatus.PLACED,
        nullable=False,
    )
    payment_method: Mapped[PaymentMethod] = mapped_column(
        Enum(PaymentMethod, name="payment_method"),
        nullable=False,
    )
    payment_status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus, name="payment_status"),
        default=PaymentStatus.PENDING,
        nullable=False,
    )

    item_total: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    discount_amount: Mapped[float] = mapped_column(
        Numeric(10, 2), default=0, nullable=False
    )
    packaging_fee: Mapped[float] = mapped_column(
        Numeric(10, 2), default=0, nullable=False
    )
    delivery_fee: Mapped[float] = mapped_column(
        Numeric(10, 2), default=0, nullable=False
    )
    platform_fee: Mapped[float] = mapped_column(
        Numeric(10, 2), default=5, nullable=False
    )
    gst_amount: Mapped[float] = mapped_column(
        Numeric(10, 2), default=0, nullable=False
    )
    tip_amount: Mapped[float] = mapped_column(
        Numeric(10, 2), default=0, nullable=False
    )
    grand_total: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False
    )

    delivery_otp: Mapped[str] = mapped_column(String(4), nullable=False)
    otp_attempts: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    otp_locked: Mapped[bool] = mapped_column(
        default=False, nullable=False
    )

    rejection_reason: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    cancellation_reason: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    estimated_delivery_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )