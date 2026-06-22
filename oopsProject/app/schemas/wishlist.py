"""
Wishlist schemas for request/response validation.
"""
from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseResponseSchema, BaseSchema
from app.schemas.product import ProductListResponse


class WishlistItemCreate(BaseSchema):
    """Schema for adding item to wishlist."""

    product_id: UUID = Field(..., description="Product UUID")


class WishlistItemResponse(BaseResponseSchema):
    """Schema for wishlist item response."""

    user_id: UUID
    product_id: UUID
    product: ProductListResponse
    created_at: datetime


class WishlistCountResponse(BaseSchema):
    """Schema for wishlist count response."""

    count: int = Field(..., description="Number of items in wishlist")


class WishlistCheckResponse(BaseSchema):
    """Schema for checking if product is in wishlist."""

    in_wishlist: bool = Field(..., description="Whether product is in wishlist")
    product_id: UUID
