"""
Review schemas.
"""
from typing import List, Optional
from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.base import BaseResponseSchema, BaseSchema
from app.utils.constants import MAX_RATING, MIN_RATING


class ReviewBase(BaseSchema):
    """Base review schema."""

    rating: int = Field(..., ge=MIN_RATING, le=MAX_RATING)
    title: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    """Review creation schema."""

    product_id: UUID
    order_id: Optional[UUID] = None
    images: List[str] = Field(default=[])


class ReviewUpdate(BaseSchema):
    """Review update schema."""

    rating: Optional[int] = Field(None, ge=MIN_RATING, le=MAX_RATING)
    title: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = None
    images: Optional[List[str]] = None


class ReviewResponse(BaseResponseSchema):
    """Review response schema."""

    product_id: UUID
    user_id: UUID
    order_id: Optional[UUID]
    rating: int
    title: Optional[str]
    comment: Optional[str]
    images: List[str]
    is_verified_purchase: bool
    helpful_count: int
    is_approved: bool
    user_name: Optional[str] = None
