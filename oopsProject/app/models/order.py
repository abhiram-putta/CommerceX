"""
Order, OrderItem, and OrderTracking models.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship, Mapped

from app.models.base import BaseModel
from app.utils.enums import OrderStatus, OrderType, PaymentMethod, PaymentStatus

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.product import Product
    from app.models.inventory import Inventory
    from app.models.payment import Payment
    from app.models.returns import ReturnRequest


class Order(BaseModel):
    """
    Order model representing customer orders.
    """

    __tablename__ = "orders"

    # Order identification
    order_number: Mapped[str] = Column(String(50), unique=True, nullable=False, index=True)

    # Customer and sellers
    customer_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    retailer_id: Mapped[Optional[UUID]] = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    wholesaler_id: Mapped[Optional[UUID]] = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    # Order type
    order_type: Mapped[OrderType] = Column(
        Enum(OrderType, native_enum=False),
        nullable=False,
        index=True,
    )

    # Pricing
    subtotal_amount: Mapped[float] = Column(Float, nullable=False)
    discount_amount: Mapped[float] = Column(Float, default=0.0, nullable=False)
    tax_amount: Mapped[float] = Column(Float, nullable=False)
    delivery_charge: Mapped[float] = Column(Float, default=0.0, nullable=False)
    total_amount: Mapped[float] = Column(Float, nullable=False)

    # Payment
    payment_status: Mapped[PaymentStatus] = Column(
        Enum(PaymentStatus, native_enum=False),
        nullable=False,
        default=PaymentStatus.PENDING,
        index=True,
    )

    payment_method: Mapped[PaymentMethod] = Column(
        Enum(PaymentMethod, native_enum=False),
        nullable=False,
        index=True,
    )

    payment_id: Mapped[Optional[str]] = Column(String(255), nullable=True, index=True)
    paid_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)

    # Delivery
    delivery_address: Mapped[dict] = Column(JSONB, nullable=False)
    delivery_latitude: Mapped[Optional[float]] = Column(Float, nullable=True)
    delivery_longitude: Mapped[Optional[float]] = Column(Float, nullable=True)
    scheduled_delivery_date: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)
    actual_delivery_date: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)
    delivery_notes: Mapped[Optional[str]] = Column(String, nullable=True)

    # Order status
    order_status: Mapped[OrderStatus] = Column(
        Enum(OrderStatus, native_enum=False),
        nullable=False,
        default=OrderStatus.PENDING,
        index=True,
    )

    cancellation_reason: Mapped[Optional[str]] = Column(String, nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)

    # Reminders (for offline orders)
    reminder_sent: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    reminder_date: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    customer: Mapped["User"] = relationship(
        "User",
        foreign_keys=[customer_id],
        back_populates="customer_orders",
    )

    retailer: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[retailer_id],
        back_populates="retailer_orders",
    )

    wholesaler: Mapped[Optional["User"]] = relationship(
        "User",
        foreign_keys=[wholesaler_id],
        back_populates="wholesaler_orders",
    )

    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    tracking: Mapped[list["OrderTracking"]] = relationship(
        "OrderTracking",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    payment: Mapped[Optional["Payment"]] = relationship(
        "Payment",
        back_populates="order",
        uselist=False,
    )

    return_requests: Mapped[list["ReturnRequest"]] = relationship(
        "ReturnRequest",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Order(number={self.order_number}, status={self.order_status}, total={self.total_amount})>"

    @property
    def is_paid(self) -> bool:
        """Check if order is paid."""
        return self.payment_status == PaymentStatus.COMPLETED

    @property
    def is_delivered(self) -> bool:
        """Check if order is delivered."""
        return self.order_status == OrderStatus.DELIVERED

    @property
    def is_cancelled(self) -> bool:
        """Check if order is cancelled."""
        return self.order_status == OrderStatus.CANCELLED


class OrderItem(BaseModel):
    """
    Order item model representing individual products in an order.
    """

    __tablename__ = "order_items"

    # Order reference
    order_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Product reference
    product_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Inventory reference
    inventory_id: Mapped[Optional[UUID]] = Column(
        UUID(as_uuid=True),
        ForeignKey("inventory.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Item details (snapshots for historical accuracy)
    product_name: Mapped[str] = Column(String(255), nullable=False)
    quantity: Mapped[int] = Column(Integer, nullable=False)
    unit_price: Mapped[float] = Column(Float, nullable=False)
    discount_percentage: Mapped[float] = Column(Float, default=0.0, nullable=False)
    total_price: Mapped[float] = Column(Float, nullable=False)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product: Mapped["Product"] = relationship("Product", back_populates="order_items")
    inventory: Mapped[Optional["Inventory"]] = relationship("Inventory")

    def __repr__(self) -> str:
        return f"<OrderItem(order_id={self.order_id}, product={self.product_name}, qty={self.quantity})>"

    @property
    def discount_amount(self) -> float:
        """Calculate discount amount for this item."""
        return self.unit_price * self.quantity * (self.discount_percentage / 100)


class OrderTracking(BaseModel):
    """
    Order tracking model for status history and location updates.
    """

    __tablename__ = "order_tracking"

    # Order reference
    order_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Status and location
    status: Mapped[str] = Column(String(100), nullable=False)
    location: Mapped[Optional[str]] = Column(String(255), nullable=True)
    latitude: Mapped[Optional[float]] = Column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = Column(Float, nullable=True)

    # Additional details
    notes: Mapped[Optional[str]] = Column(String, nullable=True)
    updated_by: Mapped[Optional[UUID]] = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    timestamp: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="tracking")

    def __repr__(self) -> str:
        return f"<OrderTracking(order_id={self.order_id}, status={self.status}, time={self.timestamp})>"
