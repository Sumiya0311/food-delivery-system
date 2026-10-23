from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.order import Order
from sqlalchemy import CheckConstraint, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base, TimestampMixin


class OrderItem(Base, TimestampMixin):
    __tablename__ = "order_items"

    __table_args__ = (
        CheckConstraint(
            "quantity BETWEEN 1 AND 10",
            name="ck_order_item_quantity",
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="ck_order_item_unit_price",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    menu_item_id: Mapped[int] = mapped_column(
        ForeignKey("menu_items.id"),
        nullable=False,
    )

    
    item_name: Mapped[str] = mapped_column(
        String(150), nullable=False
    )
    unit_price: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    quantity: Mapped[int] = mapped_column(
        nullable=False
    )
    order: Mapped["Order"] = relationship(
        "Order",
        back_populates="items",
    )