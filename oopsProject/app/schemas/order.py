"""
Order schemas.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseResponseSchema, BaseSchema
from app.utils.enums import OrderStatus, OrderType, PaymentMethod, PaymentStatus


class OrderItemCreate(BaseSchema):
    """Order item creation schema."""

    product_id: UUID
    inventory_id: UUID
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseSchema):
    """Order creation schema."""

    items: List[OrderItemCreate] = Field(..., min_length=1)
    order_type: OrderType = OrderType.ONLINE
    payment_method: PaymentMethod
    delivery_address: dict
    delivery_notes: Optional[str] = None
    scheduled_delivery_date: Optional[datetime] = None


class OrderItemResponse(BaseResponseSchema):
    """Order item response schema."""

    order_id: UUID
    product_id: UUID
    product_name: str
    quantity: int
    unit_price: float
    discount_percentage: float
    total_price: float


class OrderTrackingResponse(BaseResponseSchema):
    """Order tracking response schema."""

    order_id: UUID
    status: str
    location: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    notes: Optional[str]
    timestamp: datetime


class OrderResponse(BaseResponseSchema):
    """Order response schema."""

    order_number: str
    customer_id: UUID
    retailer_id: Optional[UUID]
    wholesaler_id: Optional[UUID]
    order_type: OrderType
    subtotal_amount: float
    discount_amount: float
    tax_amount: float
    delivery_charge: float
    total_amount: float
    payment_status: PaymentStatus
    payment_method: PaymentMethod
    payment_id: Optional[str]
    paid_at: Optional[datetime]
    delivery_address: dict
    scheduled_delivery_date: Optional[datetime]
    actual_delivery_date: Optional[datetime]
    order_status: OrderStatus
    cancellation_reason: Optional[str]
    items: List[OrderItemResponse] = []
    tracking: List[OrderTrackingResponse] = []


class OrderCancellation(BaseSchema):
    """Order cancellation schema."""

    reason: str = Field(..., min_length=10, max_length=500)
