"""
Inventory schemas for API requests and responses.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.utils.enums import OwnerType


class InventoryCreate(BaseModel):
    """Schema for creating inventory."""
    product_id: UUID
    stock_quantity: int = Field(..., ge=0)
    price: float = Field(..., gt=0)
    min_order_quantity: int = Field(1, ge=1)
    max_order_quantity: Optional[int] = Field(None, ge=1)


class InventoryUpdate(BaseModel):
    """Schema for updating inventory."""
    stock_quantity: Optional[int] = Field(None, ge=0)
    price: Optional[float] = Field(None, gt=0)
    min_order_quantity: Optional[int] = Field(None, ge=1)
    max_order_quantity: Optional[int] = Field(None, ge=1)


class InventoryResponse(BaseModel):
    """Schema for inventory response."""
    id: UUID
    product_id: UUID
    owner_id: UUID
    owner_type: OwnerType
    stock_quantity: int
    price: float
    min_order_quantity: int
    max_order_quantity: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
