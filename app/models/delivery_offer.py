from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base, TimestampMixin


class DeliveryOffer(Base, TimestampMixin):
    __tablename__ = "delivery_offers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"),
        nullable=False,
        index=True,
    )

    partner_id: Mapped[int] = mapped_column(
        ForeignKey("delivery_partners.id"),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(20), default="Pending", nullable=False
    )

    offered_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )

    responded_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )