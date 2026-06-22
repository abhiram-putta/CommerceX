"""
Inventory and Stock Alert models.
"""
from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Column, Date, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped

from app.models.base import BaseModel
from app.utils.enums import OwnerType, StockAlertType

if TYPE_CHECKING:
    from app.models.product import Product
    from app.models.user import User


class Inventory(BaseModel):
    """
    Inventory model for tracking stock by retailers and wholesalers.
    """

    __tablename__ = "inventory"

    # Product and Owner
    product_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    owner_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    owner_type: Mapped[OwnerType] = Column(
        Enum(OwnerType, native_enum=False),
        nullable=False,
        index=True,
    )

    # Stock Management
    quantity_available: Mapped[int] = Column(Integer, default=0, nullable=False)
    reorder_level: Mapped[int] = Column(Integer, default=10, nullable=False)
    reorder_quantity: Mapped[int] = Column(Integer, default=50, nullable=False)
    reserved_quantity: Mapped[int] = Column(Integer, default=0, nullable=False)

    # Pricing Override (can override product.base_price)
    price: Mapped[Optional[float]] = Column(Float, nullable=True)
    discount_percentage: Mapped[float] = Column(Float, default=0.0, nullable=False)

    # Availability
    is_available: Mapped[bool] = Column(Boolean, default=True, nullable=False, index=True)
    expected_restock_date: Mapped[Optional[date]] = Column(Date, nullable=True)
    last_restocked_at: Mapped[Optional[datetime]] = Column(DateTime, nullable=True)

    # Location
    warehouse_location: Mapped[Optional[str]] = Column(String(255), nullable=True)
    shelf_location: Mapped[Optional[str]] = Column(String(100), nullable=True)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="inventory_items")
    owner: Mapped["User"] = relationship("User", back_populates="inventory_items")

    stock_alerts: Mapped[list["StockAlert"]] = relationship(
        "StockAlert",
        back_populates="inventory",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Inventory(id={self.id}, product_id={self.product_id}, available={self.quantity_available})>"

    @property
    def effective_price(self) -> float:
        """Get effective price (override or product base price)."""
        if self.price is not None:
            return self.price
        return self.product.base_price if self.product else 0.0

    @property
    def is_low_stock(self) -> bool:
        """Check if stock is below reorder level."""
        return self.quantity_available <= self.reorder_level

    @property
    def is_out_of_stock(self) -> bool:
        """Check if stock is depleted."""
        return self.quantity_available == 0

    @property
    def available_for_sale(self) -> int:
        """Get quantity available for sale (excluding reserved)."""
        return max(0, self.quantity_available - self.reserved_quantity)


class StockAlert(BaseModel):
    """
    Stock alert model for tracking inventory alerts.
    """

    __tablename__ = "stock_alerts"

    # Inventory reference
    inventory_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("inventory.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Alert details
    alert_type: Mapped[StockAlertType] = Column(
        Enum(StockAlertType, native_enum=False),
        nullable=False,
    )

    triggered_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)
    is_resolved: Mapped[bool] = Column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    inventory: Mapped["Inventory"] = relationship("Inventory", back_populates="stock_alerts")

    def __repr__(self) -> str:
        return f"<StockAlert(id={self.id}, type={self.alert_type}, resolved={self.is_resolved})>"
