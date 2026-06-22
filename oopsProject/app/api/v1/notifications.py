"""
Notification management endpoints.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.config.database import get_db
from app.models.user import User
from app.repositories.notification_repository import NotificationRepository
from app.schemas.common import MessageResponse
from app.schemas.notification import NotificationResponse
from app.services.notification_service import NotificationService
from app.utils.enums import NotificationType

router = APIRouter()


def get_notification_service(db: AsyncSession = Depends(get_db)) -> NotificationService:
    """Get notification service dependency."""
    return NotificationService(NotificationRepository(db))


@router.get("", response_model=List[NotificationResponse])
async def get_notifications(
    unread_only: bool = Query(False, description="Only unread notifications"),
    notification_type: Optional[NotificationType] = Query(None, description="Filter by type"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    notification_service: NotificationService = Depends(get_notification_service),
) -> List[NotificationResponse]:
    """
    Get notifications for current user.

    - **unread_only**: Filter for unread notifications only
    - **notification_type**: Filter by notification type (ORDER_UPDATE, PAYMENT, PROMOTION, etc.)
    - **page**: Page number
    - **page_size**: Items per page

    Returns notifications in descending order (newest first).
    """
    skip = (page - 1) * page_size
    notifications = await notification_service.get_user_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        notification_type=notification_type,
        skip=skip,
        limit=page_size
    )
    return [NotificationResponse.model_validate(n) for n in notifications]


@router.get("/unread-count", response_model=dict)
async def get_unread_count(
    current_user: User = Depends(get_current_active_user),
    notification_service: NotificationService = Depends(get_notification_service),
) -> dict:
    """
    Get count of unread notifications (useful for notification badge).

    Returns:
    ```json
    {
      "count": 5
    }
    ```
    """
    count = await notification_service.get_unread_count(current_user.id)
    return {"count": count}


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: UUID,
    current_user: User = Depends(get_current_active_user),
    notification_service: NotificationService = Depends(get_notification_service),
) -> NotificationResponse:
    """
    Mark a specific notification as read.

    - **notification_id**: Notification UUID

    Returns the updated notification.
    """
    notification = await notification_service.mark_as_read(
        notification_id=notification_id,
        user_id=current_user.id
    )
    return NotificationResponse.model_validate(notification)


@router.put("/mark-all-read", response_model=MessageResponse)
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_active_user),
    notification_service: NotificationService = Depends(get_notification_service),
) -> MessageResponse:
    """
    Mark all notifications as read for the current user.

    Returns the count of notifications that were updated.
    """
    count = await notification_service.mark_all_as_read(current_user.id)
    return MessageResponse(message=f"{count} notifications marked as read")


@router.delete("/{notification_id}", response_model=MessageResponse)
async def delete_notification(
    notification_id: UUID,
    current_user: User = Depends(get_current_active_user),
    notification_service: NotificationService = Depends(get_notification_service),
) -> MessageResponse:
    """
    Delete a specific notification.

    - **notification_id**: Notification UUID

    Only the notification owner can delete it.
    """
    success = await notification_service.delete_notification(
        notification_id=notification_id,
        user_id=current_user.id
    )

    if not success:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Notification not found")

    return MessageResponse(message="Notification deleted successfully")


@router.delete("", response_model=MessageResponse)
async def delete_all_notifications(
    current_user: User = Depends(get_current_active_user),
    notification_service: NotificationService = Depends(get_notification_service),
) -> MessageResponse:
    """
    Delete all notifications for the current user.

    Returns the count of notifications that were deleted.
    """
    count = await notification_service.delete_all_notifications(current_user.id)
    return MessageResponse(message=f"{count} notifications deleted")
