from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base, TimestampMixin


class OrderStatusHistory(Base, TimestampMixin):
    __tablename__ = "order_status_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    changed_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    changed_by_role: Mapped[str] = mapped_column(
        String(50), default="System", nullable=False
    )

    note: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )