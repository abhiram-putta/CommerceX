"""
Shopping cart model.
"""
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.product import Product
    from app.models.inventory import Inventory


class Cart(BaseModel):
    """
    Shopping cart model for storing user cart items.
    """

    __tablename__ = "carts"

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

    # Inventory reference (specific seller)
    inventory_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("inventory.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Cart item details
    quantity: Mapped[int] = Column(Integer, nullable=False)
    price_at_addition: Mapped[float] = Column(Float, nullable=False)  # Price snapshot
    is_active: Mapped[bool] = Column(Boolean, default=True, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="carts")
    product: Mapped["Product"] = relationship("Product", back_populates="cart_items")
    inventory: Mapped["Inventory"] = relationship("Inventory")

    def __repr__(self) -> str:
        return f"<Cart(user_id={self.user_id}, product_id={self.product_id}, qty={self.quantity})>"

    @property
    def subtotal(self) -> float:
        """Calculate subtotal for this cart item."""
        return self.price_at_addition * self.quantity
