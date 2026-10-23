from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base, TimestampMixin


class MenuItem(Base, TimestampMixin):
    __tablename__ = "menu_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    restaurant_id: Mapped[int] = mapped_column(
        ForeignKey("restaurants.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)

    price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    is_available: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )