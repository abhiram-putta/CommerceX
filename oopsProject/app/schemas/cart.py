"""
Cart schemas.
"""
from typing import List
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseResponseSchema, BaseSchema


class CartItemBase(BaseSchema):
    """Base cart item schema."""

    product_id: UUID
    inventory_id: UUID
    quantity: int = Field(..., gt=0)


class CartItemCreate(CartItemBase):
    """Cart item creation schema."""

    pass


class CartItemUpdate(BaseSchema):
    """Cart item update schema."""

    quantity: int = Field(..., gt=0)


class CartItemResponse(BaseResponseSchema):
    """Cart item response schema."""

    user_id: UUID
    product_id: UUID
    inventory_id: UUID
    quantity: int
    price_at_addition: float
    is_active: bool

    @property
    def subtotal(self) -> float:
        """Calculate subtotal."""
        return self.price_at_addition * self.quantity


class CartResponse(BaseSchema):
    """Complete cart response."""

    items: List[CartItemResponse]
    total_items: int
    subtotal: float
    estimated_tax: float
    estimated_total: float

    @classmethod
    def create(cls, items: List[CartItemResponse], tax_rate: float = 0.18) -> "CartResponse":
        """Create cart response with calculations."""
        total_items = len(items)
        subtotal = sum(item.subtotal for item in items)
        estimated_tax = subtotal * tax_rate
        estimated_total = subtotal + estimated_tax

        return cls(
            items=items,
            total_items=total_items,
            subtotal=subtotal,
            estimated_tax=estimated_tax,
            estimated_total=estimated_total,
        )
