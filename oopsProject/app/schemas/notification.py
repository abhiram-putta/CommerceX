"""
Notification schemas for API requests and responses.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.utils.enums import NotificationType


class NotificationResponse(BaseModel):
    """Schema for notification response."""
    id: UUID
    user_id: UUID
    title: str
    message: str
    notification_type: NotificationType
    related_id: Optional[UUID] = None
    action_url: Optional[str] = None
    is_read: bool
    metadata: dict = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
