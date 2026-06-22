"""
Retailer-Wholesaler relationship model.
"""
from typing import Optional

from sqlalchemy import Boolean, Column, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped

from app.models.base import BaseModel


class RetailerWholesalerLink(BaseModel):
    """
    Model representing business relationship between retailers and wholesalers.
    """

    __tablename__ = "retailer_wholesaler_links"

    # Relationship parties
    retailer_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    wholesaler_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationship details
    is_active: Mapped[bool] = Column(Boolean, default=True, nullable=False)
    credit_limit: Mapped[float] = Column(Float, default=0.0, nullable=False)
    payment_terms: Mapped[Optional[str]] = Column(String(255), nullable=True)
    discount_percentage: Mapped[float] = Column(Float, default=0.0, nullable=False)

    def __repr__(self) -> str:
        return f"<RetailerWholesalerLink(retailer={self.retailer_id}, wholesaler={self.wholesaler_id})>"
