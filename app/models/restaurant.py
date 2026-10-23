from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base, TimestampMixin


class Restaurant(Base, TimestampMixin):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str] = mapped_column(String(255), nullable=False)

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    delivery_radius_km: Mapped[float] = mapped_column(
        Float, default=5.0, nullable=False
    )

    opening_time: Mapped[str] = mapped_column(Time, nullable=False)
    closing_time: Mapped[str] = mapped_column(Time, nullable=False)

    is_open: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    average_rating: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False
    )
    estimated_prep_minutes: Mapped[int] = mapped_column(
        Integer, default=30, nullable=False
    )