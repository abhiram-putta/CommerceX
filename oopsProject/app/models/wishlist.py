"""
Wishlist model for saving favorite products.
"""
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.product import Product


class Wishlist(BaseModel):
    """
    Wishlist model for users to save products they're interested in.
    """

    __tablename__ = "wishlists"
    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', name='uq_user_product_wishlist'),
    )

    # User reference
    user_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Product reference
    product_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="wishlist_items")
    product: Mapped["Product"] = relationship("Product")

    def __repr__(self) -> str:
        return f"<Wishlist(user_id={self.user_id}, product_id={self.product_id})>"
