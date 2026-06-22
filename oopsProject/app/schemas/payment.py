"""
Payment schemas.
"""
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseResponseSchema, BaseSchema
from app.utils.enums import PaymentStatus


class PaymentInitiate(BaseSchema):
    """Payment initiation schema."""

    order_id: UUID
    return_url: Optional[str] = None


class PaymentVerify(BaseSchema):
    """Payment verification schema."""

    payment_id: str
    payment_gateway_id: str
    signature: str


class PaymentResponse(BaseResponseSchema):
    """Payment response schema."""

    order_id: UUID
    payment_gateway: str
    payment_gateway_id: Optional[str]
    amount: float
    currency: str
    status: PaymentStatus
    payment_method: Optional[str]
    failure_reason: Optional[str]
    metadata: dict


class RefundRequest(BaseSchema):
    """Refund request schema."""

    payment_id: UUID
    amount: Optional[float] = Field(None, gt=0, description="Partial refund amount")
    reason: str = Field(..., min_length=10, max_length=500)
