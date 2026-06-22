"""
Payment model for transaction tracking.
"""
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Column, Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship, Mapped

from app.models.base import BaseModel
from app.utils.enums import PaymentStatus

if TYPE_CHECKING:
    from app.models.order import Order


class Payment(BaseModel):
    """
    Payment model for tracking payment transactions.
    """

    __tablename__ = "payments"

    # Order reference
    order_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Payment gateway details
    payment_gateway: Mapped[str] = Column(String(50), nullable=False)
    payment_gateway_id: Mapped[Optional[str]] = Column(String(255), nullable=True, index=True)

    # Amount
    amount: Mapped[float] = Column(Float, nullable=False)
    currency: Mapped[str] = Column(String(10), default="INR", nullable=False)

    # Status
    status: Mapped[PaymentStatus] = Column(
        Enum(PaymentStatus, native_enum=False),
        nullable=False,
        default=PaymentStatus.PENDING,
    )

    # Payment method
    payment_method: Mapped[Optional[str]] = Column(String(50), nullable=True)

    # Failure details
    failure_reason: Mapped[Optional[str]] = Column(String, nullable=True)

    # Additional metadata (renamed to avoid SQLAlchemy reserved word)
    payment_metadata: Mapped[dict] = Column(JSONB, default={}, nullable=False)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="payment")

    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, order_id={self.order_id}, status={self.status}, amount={self.amount})>"

    @property
    def is_successful(self) -> bool:
        """Check if payment was successful."""
        return self.status == PaymentStatus.COMPLETED

    @property
    def is_failed(self) -> bool:
        """Check if payment failed."""
        return self.status == PaymentStatus.FAILED
