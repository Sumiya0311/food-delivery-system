from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.cart_item import CartItem

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base, TimestampMixin


class Cart(Base, TimestampMixin):
    __tablename__ = "carts"

    __table_args__ = (
        UniqueConstraint("customer_id", name="uq_cart_customer"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    restaurant_id: Mapped[int | None] = mapped_column(
        ForeignKey("restaurants.id"),
        nullable=True,
    )

    items: Mapped[list["CartItem"]] = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan",
    )