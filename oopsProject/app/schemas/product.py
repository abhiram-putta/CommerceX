"""
Product schemas.
"""
from typing import List, Optional
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseResponseSchema, BaseSchema


class ProductBase(BaseSchema):
    """Base product schema."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str
    short_description: Optional[str] = Field(None, max_length=500)
    category_id: UUID
    base_price: float = Field(..., gt=0)
    mrp: Optional[float] = Field(None, gt=0)
    discount_percentage: float = Field(default=0.0, ge=0, le=100)
    brand: Optional[str] = Field(None, max_length=100)
    manufacturer: Optional[str] = Field(None, max_length=255)
    unit_type: str = Field(..., max_length=50)
    unit_value: float = Field(default=1.0, gt=0)


class ProductCreate(ProductBase):
    """Product creation schema."""

    images: List[str] = Field(default=[])
    is_local_product: bool = False
    region_tags: Optional[List[str]] = None
    origin_location: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    weight: Optional[float] = Field(None, gt=0)
    dimensions: Optional[dict] = None
    specifications: dict = Field(default={})
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[List[str]] = None


class ProductUpdate(BaseSchema):
    """Product update schema."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    category_id: Optional[UUID] = None
    base_price: Optional[float] = Field(None, gt=0)
    mrp: Optional[float] = Field(None, gt=0)
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
    unit_type: Optional[str] = None
    unit_value: Optional[float] = Field(None, gt=0)
    images: Optional[List[str]] = None
    is_local_product: Optional[bool] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    specifications: Optional[dict] = None


class ProductResponse(BaseResponseSchema):
    """Product response schema."""

    name: str
    slug: str
    description: str
    short_description: Optional[str]
    category_id: UUID
    base_price: float
    mrp: Optional[float]
    discount_percentage: float
    brand: Optional[str]
    manufacturer: Optional[str]
    unit_type: str
    unit_value: float
    images: List[str]
    thumbnail_url: Optional[str]
    video_url: Optional[str]
    is_local_product: bool
    region_tags: Optional[List[str]]
    origin_location: Optional[str]
    sku: Optional[str]
    barcode: Optional[str]
    weight: Optional[float]
    dimensions: Optional[dict]
    specifications: dict
    is_active: bool
    is_featured: bool
    view_count: int
    purchase_count: int
    average_rating: float
    review_count: int

    @property
    def final_price(self) -> float:
        """Calculate final price after discount."""
        if self.discount_percentage > 0:
            return self.base_price * (1 - self.discount_percentage / 100)
        return self.base_price


class ProductListResponse(BaseSchema):
    """Simplified product response for list views."""

    id: UUID
    name: str
    slug: str
    short_description: Optional[str]
    base_price: float
    discount_percentage: float
    final_price: float
    thumbnail_url: Optional[str]
    brand: Optional[str]
    average_rating: float
    review_count: int
    is_featured: bool
    is_local_product: bool
