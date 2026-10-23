from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base, TimestampMixin
from app.models.cart import Cart


class CartItem(Base, TimestampMixin):
    __tablename__ = "cart_items"

    __table_args__ = (
        UniqueConstraint(
            "cart_id",
            "menu_item_id",
            name="uq_cart_item_menu_item",
        ),
        CheckConstraint(
            "quantity BETWEEN 1 AND 10",
            name="ck_cart_item_quantity",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    cart_id: Mapped[int] = mapped_column(
        ForeignKey("carts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    menu_item_id: Mapped[int] = mapped_column(
        ForeignKey("menu_items.id"),
        nullable=False,
        index=True,
    )

    quantity: Mapped[int] = mapped_column(
        default=1,
        nullable=False,
    )

    cart: Mapped["Cart"] = relationship(
        "Cart",
        back_populates="items",
    )