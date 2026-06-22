"""
Product model for the e-commerce catalog.
"""
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, ARRAY
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship, Mapped

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.category import Category
    from app.models.cart import Cart
    from app.models.inventory import Inventory
    from app.models.order import OrderItem
    from app.models.review import Review
    from app.models.interaction import UserInteraction


class Product(BaseModel):
    """
    Product model with comprehensive product information.
    """

    __tablename__ = "products"

    # Basic Information
    name: Mapped[str] = Column(String(255), nullable=False, index=True)
    slug: Mapped[str] = Column(String(255), unique=True, nullable=False, index=True)
    description: Mapped[str] = Column(String, nullable=False)
    short_description: Mapped[Optional[str]] = Column(String(500), nullable=True)

    # Category
    category_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    # Pricing
    base_price: Mapped[float] = Column(Float, nullable=False)
    mrp: Mapped[Optional[float]] = Column(Float, nullable=True)
    discount_percentage: Mapped[float] = Column(Float, default=0.0, nullable=False)

    # Product Details
    brand: Mapped[Optional[str]] = Column(String(100), nullable=True, index=True)
    manufacturer: Mapped[Optional[str]] = Column(String(255), nullable=True)
    unit_type: Mapped[str] = Column(String(50), nullable=False)  # kg, liter, piece, etc.
    unit_value: Mapped[float] = Column(Float, default=1.0, nullable=False)

    # Media
    images: Mapped[list] = Column(JSONB, default=[], nullable=False)
    thumbnail_url: Mapped[Optional[str]] = Column(String(500), nullable=True)
    video_url: Mapped[Optional[str]] = Column(String(500), nullable=True)

    # Regional/Local
    is_local_product: Mapped[bool] = Column(Boolean, default=False, nullable=False, index=True)
    region_tags: Mapped[Optional[list]] = Column(ARRAY(String), nullable=True)
    origin_location: Mapped[Optional[str]] = Column(String(255), nullable=True)

    # Additional Information
    sku: Mapped[Optional[str]] = Column(String(100), unique=True, nullable=True)
    barcode: Mapped[Optional[str]] = Column(String(100), nullable=True)
    weight: Mapped[Optional[float]] = Column(Float, nullable=True)  # in kg
    dimensions: Mapped[Optional[dict]] = Column(JSONB, nullable=True)
    specifications: Mapped[dict] = Column(JSONB, default={}, nullable=False)

    # SEO
    meta_title: Mapped[Optional[str]] = Column(String(255), nullable=True)
    meta_description: Mapped[Optional[str]] = Column(String(500), nullable=True)
    meta_keywords: Mapped[Optional[list]] = Column(ARRAY(String), nullable=True)

    # Status & Stats
    is_active: Mapped[bool] = Column(Boolean, default=True, nullable=False, index=True)
    is_featured: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    view_count: Mapped[int] = Column(Integer, default=0, nullable=False)
    purchase_count: Mapped[int] = Column(Integer, default=0, nullable=False)
    average_rating: Mapped[float] = Column(Float, default=0.0, nullable=False)
    review_count: Mapped[int] = Column(Integer, default=0, nullable=False)

    # Relationships
    category: Mapped["Category"] = relationship("Category", back_populates="products")

    inventory_items: Mapped[list["Inventory"]] = relationship(
        "Inventory",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    cart_items: Mapped[list["Cart"]] = relationship(
        "Cart",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="product",
    )

    reviews: Mapped[list["Review"]] = relationship(
        "Review",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    interactions: Mapped[list["UserInteraction"]] = relationship(
        "UserInteraction",
        back_populates="product",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name={self.name}, price={self.base_price})>"

    @property
    def final_price(self) -> float:
        """Calculate final price after discount."""
        if self.discount_percentage > 0:
            return self.base_price * (1 - self.discount_percentage / 100)
        return self.base_price

    @property
    def discount_amount(self) -> float:
        """Calculate discount amount."""
        if self.discount_percentage > 0:
            return self.base_price * (self.discount_percentage / 100)
        return 0.0

    @property
    def is_in_stock(self) -> bool:
        """Check if product has any available inventory."""
        return any(
            item.is_available and item.quantity_available > 0
            for item in self.inventory_items
        )
