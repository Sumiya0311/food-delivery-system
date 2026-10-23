from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base, TimestampMixin


class Coupon(Base, TimestampMixin):
    __tablename__ = "coupons"

    __table_args__ = (
        CheckConstraint(
            "discount_value > 0",
            name="ck_coupon_discount_positive",
        ),
        CheckConstraint(
            "min_order_amount >= 0",
            name="ck_coupon_min_order_nonnegative",
        ),
        CheckConstraint(
            "usage_limit IS NULL OR usage_limit > 0",
            name="ck_coupon_usage_limit_positive",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    code: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )

    restaurant_id: Mapped[int | None] = mapped_column(
        ForeignKey("restaurants.id"),
        nullable=True,
        index=True,
    )

    created_by_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    discount_type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )
    discount_value: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    min_order_amount: Mapped[float] = mapped_column(
        Numeric(10, 2), default=0, nullable=False
    )
    max_discount: Mapped[float | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )

    usage_limit: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )
    used_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    per_user_limit: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False
    )

    first_order_only: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    starts_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )