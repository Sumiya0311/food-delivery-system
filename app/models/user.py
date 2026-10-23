import enum

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base, TimestampMixin


class UserRole(str, enum.Enum):
    ADMIN = "Admin"
    RESTAURANT_OWNER = "Restaurant Owner"
    DELIVERY_PARTNER = "Delivery Partner"
    CUSTOMER = "Customer"


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    phone: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        default=UserRole.CUSTOMER,
        nullable=False,
    )

    is_approved: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )