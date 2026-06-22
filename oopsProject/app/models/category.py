"""
Category model for product categorization.
"""
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.product import Product


class Category(BaseModel):
    """
    Product category model with hierarchical structure.
    Supports parent-child relationships for subcategories.
    """

    __tablename__ = "categories"

    # Basic Information
    name: Mapped[str] = Column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = Column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = Column(String, nullable=True)

    # Hierarchy (self-referential)
    parent_id: Mapped[Optional[UUID]] = Column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Media
    image_url: Mapped[Optional[str]] = Column(String(500), nullable=True)
    icon_name: Mapped[Optional[str]] = Column(String(100), nullable=True)

    # Display
    display_order: Mapped[int] = Column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = Column(Boolean, default=True, nullable=False)
    is_featured: Mapped[bool] = Column(Boolean, default=False, nullable=False)

    # Relationships
    parent: Mapped[Optional["Category"]] = relationship(
        "Category",
        remote_side="Category.id",
        back_populates="subcategories",
    )

    subcategories: Mapped[list["Category"]] = relationship(
        "Category",
        back_populates="parent",
        cascade="all, delete-orphan",
    )

    products: Mapped[list["Product"]] = relationship(
        "Product",
        back_populates="category",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name}, slug={self.slug})>"

    @property
    def is_root(self) -> bool:
        """Check if this is a root category (no parent)."""
        return self.parent_id is None

    @property
    def level(self) -> int:
        """Get the depth level of this category in the hierarchy."""
        level = 0
        current = self
        while current.parent_id is not None:
            level += 1
            current = current.parent
        return level
