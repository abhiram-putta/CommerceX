"""
Coupon and discount models.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Boolean, Column, Date, DateTime, Enum, Float, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped

from app.models.base import BaseModel
from app.utils.enums import CouponType, DiscountType

if TYPE_CHECKING:
    pass


class Coupon(BaseModel):
    """
    Coupon model for discount codes.
    """

    __tablename__ = "coupons"

    # Basic Information
    code: Mapped[str] = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique coupon code"
    )
    name: Mapped[str] = Column(String(255), nullable=False, comment="Coupon name/description")

    # Discount Details
    discount_type: Mapped[DiscountType] = Column(
        Enum(DiscountType, native_enum=False),
        nullable=False,
        comment="Percentage or fixed amount"
    )
    discount_value: Mapped[float] = Column(
        Float,
        nullable=False,
        comment="Discount percentage or fixed amount"
    )
    max_discount_amount: Mapped[Optional[float]] = Column(
        Float,
        nullable=True,
        comment="Maximum discount amount (for percentage discounts)"
    )

    # Coupon Type
    coupon_type: Mapped[CouponType] = Column(
        Enum(CouponType, native_enum=False),
        nullable=False,
        default=CouponType.GENERAL,
        comment="General, first-time user, or product-specific"
    )

    # Conditions
    minimum_order_amount: Mapped[Optional[float]] = Column(
        Float,
        nullable=True,
        comment="Minimum order amount to apply coupon"
    )
    maximum_order_amount: Mapped[Optional[float]] = Column(
        Float,
        nullable=True,
        comment="Maximum order amount to apply coupon"
    )

    # Usage Limits
    usage_limit: Mapped[Optional[int]] = Column(
        Integer,
        nullable=True,
        comment="Total times coupon can be used (null = unlimited)"
    )
    usage_limit_per_user: Mapped[Optional[int]] = Column(
        Integer,
        nullable=True,
        comment="Times each user can use coupon (null = unlimited)"
    )
    used_count: Mapped[int] = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of times coupon has been used"
    )

    # Validity Period
    valid_from: Mapped[datetime] = Column(
        DateTime,
        nullable=False,
        comment="Coupon valid from this date"
    )
    valid_until: Mapped[datetime] = Column(
        DateTime,
        nullable=False,
        comment="Coupon valid until this date"
    )

    # Product/Category Restrictions
    applicable_products: Mapped[Optional[list]] = Column(
        JSONB,
        nullable=True,
        comment="List of product IDs (null = all products)"
    )
    applicable_categories: Mapped[Optional[list]] = Column(
        JSONB,
        nullable=True,
        comment="List of category IDs (null = all categories)"
    )

    # User Restrictions
    applicable_users: Mapped[Optional[list]] = Column(
        JSONB,
        nullable=True,
        comment="List of user IDs (null = all users)"
    )
    first_time_users_only: Mapped[bool] = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Only for users with no previous orders"
    )

    # Status
    is_active: Mapped[bool] = Column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
        comment="Is coupon active"
    )
    is_stackable: Mapped[bool] = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Can be combined with other coupons"
    )

    # Additional Fields
    description: Mapped[Optional[str]] = Column(
        String,
        nullable=True,
        comment="Coupon description for customers"
    )
    terms_and_conditions: Mapped[Optional[str]] = Column(
        String,
        nullable=True,
        comment="Terms and conditions"
    )

    def __repr__(self) -> str:
        return f"<Coupon(code={self.code}, discount={self.discount_value})>"

    def is_valid(self) -> bool:
        """Check if coupon is currently valid."""
        now = datetime.utcnow()
        return (
            self.is_active
            and self.valid_from <= now <= self.valid_until
            and (self.usage_limit is None or self.used_count < self.usage_limit)
        )

    def can_user_use(self, user_usage_count: int) -> bool:
        """Check if user can use this coupon."""
        if self.usage_limit_per_user is None:
            return True
        return user_usage_count < self.usage_limit_per_user


class CouponUsage(BaseModel):
    """
    Track coupon usage by users.
    """

    __tablename__ = "coupon_usages"

    # Foreign Keys
    coupon_id: Mapped[UUID] = Column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="Coupon ID"
    )
    user_id: Mapped[UUID] = Column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="User ID"
    )
    order_id: Mapped[Optional[UUID]] = Column(
        PGUUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="Order ID where coupon was used"
    )

    # Usage Details
    discount_amount: Mapped[float] = Column(
        Float,
        nullable=False,
        comment="Actual discount amount applied"
    )
    order_amount: Mapped[float] = Column(
        Float,
        nullable=False,
        comment="Order amount before discount"
    )

    # Metadata
    used_at: Mapped[datetime] = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="When coupon was used"
    )

    def __repr__(self) -> str:
        return f"<CouponUsage(coupon_id={self.coupon_id}, user_id={self.user_id})>"
