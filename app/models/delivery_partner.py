from sqlalchemy import Boolean, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base, TimestampMixin


class DeliveryPartner(Base, TimestampMixin):
    __tablename__ = "delivery_partners"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )

    vehicle_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False
    )
    vehicle_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )

    is_online: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_available: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    latitude: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    longitude: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    total_earnings: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )