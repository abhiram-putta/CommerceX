"""
Notification model for user notifications.
"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ARRAY, Boolean, Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship, Mapped

from app.models.base import BaseModel
from app.utils.enums import NotificationType

if TYPE_CHECKING:
    from app.models.user import User


class Notification(BaseModel):
    """
    Notification model for storing user notifications.
    """

    __tablename__ = "notifications"

    # User reference
    user_id: Mapped[UUID] = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Notification type
    type: Mapped[NotificationType] = Column(
        Enum(NotificationType, native_enum=False),
        nullable=False,
        index=True,
    )

    # Content
    title: Mapped[str] = Column(String(255), nullable=False)
    message: Mapped[str] = Column(String, nullable=False)
    data: Mapped[dict] = Column(JSONB, default={}, nullable=False)

    # Read status
    is_read: Mapped[bool] = Column(Boolean, default=False, nullable=False, index=True)
    read_at: Mapped[Optional[datetime]] = Column(DateTime(timezone=True), nullable=True)

    # Delivery channels
    sent_via: Mapped[list] = Column(ARRAY(String), default=[], nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="notifications")

    def __repr__(self) -> str:
        return f"<Notification(user_id={self.user_id}, type={self.type}, read={self.is_read})>"

    def mark_as_read(self) -> None:
        """Mark notification as read."""
        self.is_read = True
        self.read_at = datetime.utcnow()
