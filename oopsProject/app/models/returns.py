"""
Return and refund models.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, relationship

from app.models.base import BaseModel
from app.utils.enums import ReturnReason, ReturnStatus, RefundStatus

if TYPE_CHECKING:
    from app.models.order import Order, OrderItem
    from app.models.user import User


class ReturnRequest(BaseModel):
    """
    Return request model for order returns.
    """

    __tablename__ = "return_requests"

    # Foreign Keys
    order_id: Mapped[UUID] = Column(
        PGUUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Order ID"
    )
    user_id: Mapped[UUID] = Column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID"
    )

    # Return Details
    return_number: Mapped[str] = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique return number"
    )
    reason: Mapped[ReturnReason] = Column(
        Enum(ReturnReason, native_enum=False),
        nullable=False,
        comment="Return reason"
    )
    description: Mapped[Optional[str]] = Column(
        Text,
        nullable=True,
        comment="Detailed description"
    )
    images: Mapped[Optional[list]] = Column(
        JSONB,
        nullable=True,
        comment="Images as proof (URLs)"
    )

    # Status
    status: Mapped[ReturnStatus] = Column(
        Enum(ReturnStatus, native_enum=False),
        nullable=False,
        default=ReturnStatus.REQUESTED,
        index=True,
        comment="Return status"
    )

    # Amounts
    refund_amount: Mapped[float] = Column(
        Float,
        nullable=False,
        comment="Refund amount to be processed"
    )
    refund_status: Mapped[RefundStatus] = Column(
        Enum(RefundStatus, native_enum=False),
        nullable=False,
        default=RefundStatus.PENDING,
        index=True,
        comment="Refund status"
    )

    # Items being returned (JSON array of order_item_ids)
    items: Mapped[list] = Column(
        JSONB,
        nullable=False,
        comment="List of order item IDs being returned"
    )

    # Dates
    requested_at: Mapped[datetime] = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="When return was requested"
    )
    approved_at: Mapped[Optional[datetime]] = Column(
        DateTime,
        nullable=True,
        comment="When return was approved"
    )
    rejected_at: Mapped[Optional[datetime]] = Column(
        DateTime,
        nullable=True,
        comment="When return was rejected"
    )
    completed_at: Mapped[Optional[datetime]] = Column(
        DateTime,
        nullable=True,
        comment="When return was completed"
    )

    # Pickup/Return Details
    pickup_address: Mapped[Optional[dict]] = Column(
        JSONB,
        nullable=True,
        comment="Pickup address for return"
    )
    tracking_number: Mapped[Optional[str]] = Column(
        String(100),
        nullable=True,
        comment="Tracking number for return shipment"
    )

    # Admin Notes
    admin_notes: Mapped[Optional[str]] = Column(
        Text,
        nullable=True,
        comment="Internal admin notes"
    )
    rejection_reason: Mapped[Optional[str]] = Column(
        Text,
        nullable=True,
        comment="Reason for rejection"
    )

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="return_requests")
    user: Mapped["User"] = relationship("User")

    def __repr__(self) -> str:
        return f"<ReturnRequest(return_number={self.return_number}, status={self.status})>"

    def can_be_approved(self) -> bool:
        """Check if return can be approved."""
        return self.status == ReturnStatus.REQUESTED

    def can_be_rejected(self) -> bool:
        """Check if return can be rejected."""
        return self.status == ReturnStatus.REQUESTED


class RefundTransaction(BaseModel):
    """
    Refund transaction tracking.
    """

    __tablename__ = "refund_transactions"

    # Foreign Keys
    return_request_id: Mapped[UUID] = Column(
        PGUUID(as_uuid=True),
        ForeignKey("return_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Return request ID"
    )
    order_id: Mapped[UUID] = Column(
        PGUUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Order ID"
    )

    # Transaction Details
    transaction_id: Mapped[str] = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Refund transaction ID"
    )
    amount: Mapped[float] = Column(
        Float,
        nullable=False,
        comment="Refund amount"
    )
    status: Mapped[RefundStatus] = Column(
        Enum(RefundStatus, native_enum=False),
        nullable=False,
        default=RefundStatus.PENDING,
        comment="Refund status"
    )

    # Payment Gateway Details
    gateway: Mapped[str] = Column(
        String(50),
        nullable=False,
        comment="Payment gateway (razorpay, stripe, etc.)"
    )
    gateway_refund_id: Mapped[Optional[str]] = Column(
        String(100),
        nullable=True,
        comment="Gateway refund ID"
    )
    gateway_response: Mapped[Optional[dict]] = Column(
        JSONB,
        nullable=True,
        comment="Gateway response"
    )

    # Dates
    initiated_at: Mapped[datetime] = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        comment="When refund was initiated"
    )
    processed_at: Mapped[Optional[datetime]] = Column(
        DateTime,
        nullable=True,
        comment="When refund was processed"
    )
    failed_at: Mapped[Optional[datetime]] = Column(
        DateTime,
        nullable=True,
        comment="When refund failed"
    )

    # Error Details
    error_message: Mapped[Optional[str]] = Column(
        Text,
        nullable=True,
        comment="Error message if failed"
    )

    def __repr__(self) -> str:
        return f"<RefundTransaction(transaction_id={self.transaction_id}, status={self.status})>"
