from sqlalchemy import CheckConstraint, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base, TimestampMixin


class Rating(Base, TimestampMixin):
    __tablename__ = "ratings"

    __table_args__ = (
        CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="ck_rating_range",
        ),
        UniqueConstraint(
            "order_id",
            name="uq_rating_order",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"),
        nullable=False,
    )

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True,
    )

    rating: Mapped[int] = mapped_column(
        Integer, nullable=False
    )

    review: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )