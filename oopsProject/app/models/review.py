"""
Product review and rating model.
"""
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship, Mapped

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.user import User
    from app.models.order import Order


class Review(BaseModel):
    """
    Product review model with ratings and comments.
    """

    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating_range"),
    )

    # Product and user
    product_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    user_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    order_id: Mapped[Optional[UUID]] = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Review content
    rating: Mapped[int] = Column(Integer, nullable=False)
    title: Mapped[Optional[str]] = Column(String(255), nullable=True)
    comment: Mapped[Optional[str]] = Column(String, nullable=True)
    images: Mapped[list] = Column(JSONB, default=[], nullable=False)

    # Verification and moderation
    is_verified_purchase: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    helpful_count: Mapped[int] = Column(Integer, default=0, nullable=False)
    is_approved: Mapped[bool] = Column(Boolean, default=True, nullable=False)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="reviews")
    user: Mapped["User"] = relationship("User", back_populates="reviews")
    order: Mapped[Optional["Order"]] = relationship("Order")

    def __repr__(self) -> str:
        return f"<Review(product_id={self.product_id}, user_id={self.user_id}, rating={self.rating})>"
