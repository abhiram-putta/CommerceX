"""
User interaction model for ML tracking.
"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship, Mapped

from app.models.base import BaseModel
from app.utils.enums import InteractionType

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.product import Product


class UserInteraction(BaseModel):
    """
    User interaction model for tracking user behavior for ML.
    """

    __tablename__ = "user_interactions"

    # User and product
    user_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    product_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Interaction details
    interaction_type: Mapped[InteractionType] = Column(
        Enum(InteractionType, native_enum=False),
        nullable=False,
        index=True,
    )

    session_id: Mapped[str] = Column(String(255), nullable=False, index=True)
    interaction_metadata: Mapped[dict] = Column(JSONB, default={}, nullable=False)
    timestamp: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False, index=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="interactions")
    product: Mapped["Product"] = relationship("Product", back_populates="interactions")

    def __repr__(self) -> str:
        return f"<UserInteraction(user_id={self.user_id}, product_id={self.product_id}, type={self.interaction_type})>"
