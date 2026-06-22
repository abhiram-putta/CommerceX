"""
Pydantic schemas for coupon validation.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.common import BaseSchema, BaseResponseSchema
from app.utils.enums import CouponType, DiscountType


class CouponCreate(BaseSchema):
    """Schema for creating a coupon."""

    code: str = Field(..., min_length=3, max_length=50, description="Coupon code")
    name: str = Field(..., min_length=1, max_length=255, description="Coupon name")
    discount_type: DiscountType = Field(..., description="Discount type")
    discount_value: float = Field(..., gt=0, description="Discount value")
    max_discount_amount: Optional[float] = Field(None, ge=0, description="Maximum discount amount")
    coupon_type: CouponType = Field(CouponType.GENERAL, description="Coupon type")
    minimum_order_amount: Optional[float] = Field(None, ge=0, description="Minimum order amount")
    maximum_order_amount: Optional[float] = Field(None, ge=0, description="Maximum order amount")
    usage_limit: Optional[int] = Field(None, ge=1, description="Total usage limit")
    usage_limit_per_user: Optional[int] = Field(None, ge=1, description="Usage limit per user")
    valid_from: datetime = Field(..., description="Valid from date")
    valid_until: datetime = Field(..., description="Valid until date")
    applicable_products: Optional[List[UUID]] = Field(None, description="Applicable product IDs")
    applicable_categories: Optional[List[UUID]] = Field(None, description="Applicable category IDs")
    applicable_users: Optional[List[UUID]] = Field(None, description="Applicable user IDs")
    first_time_users_only: bool = Field(False, description="Only for first-time users")
    is_stackable: bool = Field(False, description="Can be stacked with other coupons")
    description: Optional[str] = Field(None, description="Coupon description")
    terms_and_conditions: Optional[str] = Field(None, description="Terms and conditions")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        """Validate and uppercase coupon code."""
        return v.upper().strip()

    @field_validator("valid_until")
    @classmethod
    def validate_dates(cls, v: datetime, info) -> datetime:
        """Validate that valid_until is after valid_from."""
        if "valid_from" in info.data and v <= info.data["valid_from"]:
            raise ValueError("valid_until must be after valid_from")
        return v


class CouponUpdate(BaseSchema):
    """Schema for updating a coupon."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    discount_value: Optional[float] = Field(None, gt=0)
    max_discount_amount: Optional[float] = Field(None, ge=0)
    minimum_order_amount: Optional[float] = Field(None, ge=0)
    maximum_order_amount: Optional[float] = Field(None, ge=0)
    usage_limit: Optional[int] = Field(None, ge=1)
    usage_limit_per_user: Optional[int] = Field(None, ge=1)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: Optional[bool] = None
    is_stackable: Optional[bool] = None
    description: Optional[str] = None
    terms_and_conditions: Optional[str] = None


class CouponResponse(BaseResponseSchema):
    """Schema for coupon response."""

    code: str
    name: str
    discount_type: DiscountType
    discount_value: float
    max_discount_amount: Optional[float]
    coupon_type: CouponType
    minimum_order_amount: Optional[float]
    maximum_order_amount: Optional[float]
    usage_limit: Optional[int]
    usage_limit_per_user: Optional[int]
    used_count: int
    valid_from: datetime
    valid_until: datetime
    is_active: bool
    is_stackable: bool
    description: Optional[str]
    terms_and_conditions: Optional[str]


class CouponValidateRequest(BaseSchema):
    """Schema for validating a coupon."""

    code: str = Field(..., description="Coupon code")
    order_amount: float = Field(..., gt=0, description="Order amount")
    product_ids: Optional[List[UUID]] = Field(None, description="Product IDs in order")
    category_ids: Optional[List[UUID]] = Field(None, description="Category IDs in order")


class CouponValidateResponse(BaseSchema):
    """Schema for coupon validation response."""

    coupon_id: UUID
    code: str
    discount_type: DiscountType
    discount_value: float
    discount_amount: float
    final_amount: float
    message: str


class CouponUsageResponse(BaseResponseSchema):
    """Schema for coupon usage response."""

    coupon_id: UUID
    user_id: UUID
    order_id: Optional[UUID]
    discount_amount: float
    order_amount: float
    used_at: datetime
