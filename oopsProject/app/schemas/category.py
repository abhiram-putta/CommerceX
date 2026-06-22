"""
Category schemas.
"""
from typing import List, Optional
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseResponseSchema, BaseSchema


class CategoryBase(BaseSchema):
    """Base category schema."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    image_url: Optional[str] = None
    icon_name: Optional[str] = None
    display_order: int = 0


class CategoryCreate(CategoryBase):
    """Category creation schema."""

    is_active: bool = True
    is_featured: bool = False


class CategoryUpdate(BaseSchema):
    """Category update schema."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    image_url: Optional[str] = None
    icon_name: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


class CategoryResponse(BaseResponseSchema):
    """Category response schema."""

    name: str
    slug: str
    description: Optional[str]
    parent_id: Optional[UUID]
    image_url: Optional[str]
    icon_name: Optional[str]
    display_order: int
    is_active: bool
    is_featured: bool
    product_count: int = 0
    subcategories: List["CategoryResponse"] = []
