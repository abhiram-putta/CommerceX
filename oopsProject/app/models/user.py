"""
User and UserProfile models.
"""
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Column, Date, DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship, Mapped

from app.models.base import BaseModel
from app.utils.enums import Gender, UserRole

if TYPE_CHECKING:
    from app.models.cart import Cart
    from app.models.wishlist import Wishlist
    from app.models.inventory import Inventory
    from app.models.notification import Notification
    from app.models.order import Order
    from app.models.review import Review
    from app.models.interaction import UserInteraction


class User(BaseModel):
    """
    User model representing customers, retailers, and wholesalers.
    """

    __tablename__ = "users"

    # Authentication
    email: Mapped[str] = Column(String(255), unique=True, nullable=False, index=True)
    phone: Mapped[Optional[str]] = Column(String(20), unique=True, nullable=True, index=True)
    password_hash: Mapped[str] = Column(String(255), nullable=False)

    # Role
    role: Mapped[UserRole] = Column(
        Enum(UserRole, native_enum=False),
        nullable=False,
        default=UserRole.CUSTOMER,
        index=True,
    )

    # Status
    is_active: Mapped[bool] = Column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    email_verified: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    phone_verified: Mapped[bool] = Column(Boolean, default=False, nullable=False)

    # Profile completion
    profile_completion: Mapped[float] = Column(Float, default=0.0, nullable=False)

    # Last login
    last_login: Mapped[Optional[datetime]] = Column(DateTime, nullable=True)

    # Relationships
    profile: Mapped[Optional["UserProfile"]] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    carts: Mapped[list["Cart"]] = relationship(
        "Cart",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    wishlist_items: Mapped[list["Wishlist"]] = relationship(
        "Wishlist",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    customer_orders: Mapped[list["Order"]] = relationship(
        "Order",
        foreign_keys="Order.customer_id",
        back_populates="customer",
        cascade="all, delete-orphan",
    )

    retailer_orders: Mapped[list["Order"]] = relationship(
        "Order",
        foreign_keys="Order.retailer_id",
        back_populates="retailer",
    )

    wholesaler_orders: Mapped[list["Order"]] = relationship(
        "Order",
        foreign_keys="Order.wholesaler_id",
        back_populates="wholesaler",
    )

    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    interactions: Mapped[list["UserInteraction"]] = relationship(
        "UserInteraction",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    notifications: Mapped[list["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    inventory_items: Mapped[list["Inventory"]] = relationship(
        "Inventory",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


class UserProfile(BaseModel):
    """
    Extended user profile with personal and business information.
    """

    __tablename__ = "user_profiles"

    # Foreign key
    user_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Personal Information
    full_name: Mapped[Optional[str]] = Column(String(255), nullable=True)
    profile_image_url: Mapped[Optional[str]] = Column(String(500), nullable=True)
    date_of_birth: Mapped[Optional[date]] = Column(Date, nullable=True)
    gender: Mapped[Optional[str]] = Column(String(20), nullable=True)

    # Address
    address_line1: Mapped[Optional[str]] = Column(String(500), nullable=True)
    address_line2: Mapped[Optional[str]] = Column(String(500), nullable=True)
    city: Mapped[Optional[str]] = Column(String(100), nullable=True, index=True)
    state: Mapped[Optional[str]] = Column(String(100), nullable=True, index=True)
    country: Mapped[str] = Column(String(100), default="India", nullable=False)
    pincode: Mapped[Optional[str]] = Column(String(10), nullable=True, index=True)

    # Coordinates
    latitude: Mapped[Optional[float]] = Column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = Column(Float, nullable=True)

    # Business Information (for retailers/wholesalers)
    business_name: Mapped[Optional[str]] = Column(String(255), nullable=True)
    business_license: Mapped[Optional[str]] = Column(String(100), nullable=True)
    gst_number: Mapped[Optional[str]] = Column(String(50), nullable=True)
    business_type: Mapped[Optional[str]] = Column(String(100), nullable=True)
    business_description: Mapped[Optional[str]] = Column(String, nullable=True)

    # ML Personalization
    preferences: Mapped[dict] = Column(JSONB, default={}, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profile")

    def __repr__(self) -> str:
        return f"<UserProfile(user_id={self.user_id}, full_name={self.full_name})>"
