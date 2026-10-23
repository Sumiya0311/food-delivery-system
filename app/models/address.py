from sqlalchemy import Boolean, ForeignKey, String, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base, TimestampMixin


class Address(Base, TimestampMixin):
    __tablename__ = "addresses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    label: Mapped[str] = mapped_column(
        String(50), default="Home", nullable=False
    )
    recipient_name: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    phone: Mapped[str] = mapped_column(String(10), nullable=False)

    address_line: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    pincode: Mapped[str] = mapped_column(String(6), nullable=False)

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    is_default: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )