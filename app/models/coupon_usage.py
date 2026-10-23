from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base, TimestampMixin


class CouponUsage(Base, TimestampMixin):
    __tablename__ = "coupon_usages"

    __table_args__ = (
        UniqueConstraint(
            "coupon_id",
            "customer_id",
            "order_id",
            name="uq_coupon_usage_order",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    coupon_id: Mapped[int] = mapped_column(
        ForeignKey("coupons.id"),
        nullable=False,
        index=True,
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"),
        nullable=False,
        index=True,
    )