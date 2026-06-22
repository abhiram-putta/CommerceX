"""
Notification service for managing user notifications.
"""
from typing import List, Optional
from uuid import UUID

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.notification import Notification
from app.repositories.notification_repository import NotificationRepository
from app.utils.enums import NotificationType
from app.utils.logger import get_logger

logger = get_logger(__name__)


class NotificationService:
    """Notification service with business logic."""

    def __init__(self, notification_repository: NotificationRepository):
        """
        Initialize notification service.

        Args:
            notification_repository: Notification repository instance
        """
        self.notification_repository = notification_repository

    async def create_notification(
        self,
        user_id: UUID,
        title: str,
        message: str,
        notification_type: NotificationType,
        related_id: Optional[UUID] = None,
        action_url: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Notification:
        """
        Create a new notification.

        Args:
            user_id: User UUID
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            related_id: Related entity ID (order, product, etc.)
            action_url: Optional action URL
            metadata: Optional additional data

        Returns:
            Created notification
        """
        notification_data = {
            'user_id': user_id,
            'title': title,
            'message': message,
            'notification_type': notification_type,
            'related_id': related_id,
            'action_url': action_url,
            'metadata': metadata or {},
            'is_read': False
        }

        notification = await self.notification_repository.create(notification_data)
        logger.info(f"Notification created: {notification.id} for user {user_id}")

        return notification

    async def get_user_notifications(
        self,
        user_id: UUID,
        unread_only: bool = False,
        notification_type: Optional[NotificationType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Notification]:
        """
        Get notifications for a user.

        Args:
            user_id: User UUID
            unread_only: Only return unread notifications
            notification_type: Optional type filter
            skip: Skip N records
            limit: Limit results

        Returns:
            List of notifications
        """
        return await self.notification_repository.get_user_notifications(
            user_id,
            unread_only,
            notification_type,
            skip,
            limit
        )

    async def mark_as_read(
        self,
        notification_id: UUID,
        user_id: UUID
    ) -> Notification:
        """
        Mark notification as read.

        Args:
            notification_id: Notification UUID
            user_id: User UUID (for verification)

        Returns:
            Updated notification

        Raises:
            NotFoundError: If notification not found
            BadRequestError: If unauthorized
        """
        notification = await self.notification_repository.get(notification_id)

        if not notification:
            raise NotFoundError("Notification not found")

        if notification.user_id != user_id:
            raise BadRequestError("Unauthorized to modify this notification")

        updated = await self.notification_repository.mark_as_read(notification_id)
        logger.info(f"Notification marked as read: {notification_id}")

        return updated

    async def mark_all_as_read(self, user_id: UUID) -> int:
        """
        Mark all user notifications as read.

        Args:
            user_id: User UUID

        Returns:
            Number of notifications updated
        """
        count = await self.notification_repository.mark_all_as_read(user_id)
        logger.info(f"Marked {count} notifications as read for user {user_id}")

        return count

    async def get_unread_count(self, user_id: UUID) -> int:
        """
        Get count of unread notifications.

        Args:
            user_id: User UUID

        Returns:
            Unread notification count
        """
        return await self.notification_repository.get_unread_count(user_id)

    async def delete_notification(
        self,
        notification_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete a notification.

        Args:
            notification_id: Notification UUID
            user_id: User UUID (for verification)

        Returns:
            True if successful

        Raises:
            NotFoundError: If notification not found
            BadRequestError: If unauthorized
        """
        notification = await self.notification_repository.get(notification_id)

        if not notification:
            raise NotFoundError("Notification not found")

        if notification.user_id != user_id:
            raise BadRequestError("Unauthorized to delete this notification")

        success = await self.notification_repository.delete(notification_id)
        logger.info(f"Notification deleted: {notification_id}")

        return success

    async def delete_all_notifications(self, user_id: UUID) -> int:
        """
        Delete all notifications for a user.

        Args:
            user_id: User UUID

        Returns:
            Number of notifications deleted
        """
        count = await self.notification_repository.delete_user_notifications(user_id)
        logger.info(f"Deleted {count} notifications for user {user_id}")

        return count

    # Helper methods to create specific notification types

    async def notify_order_placed(self, user_id: UUID, order_id: UUID, order_number: str) -> Notification:
        """Create notification for order placement."""
        return await self.create_notification(
            user_id=user_id,
            title="Order Placed Successfully",
            message=f"Your order #{order_number} has been placed successfully.",
            notification_type=NotificationType.ORDER_UPDATE,
            related_id=order_id,
            action_url=f"/orders/{order_id}"
        )

    async def notify_order_confirmed(self, user_id: UUID, order_id: UUID, order_number: str) -> Notification:
        """Create notification for order confirmation."""
        return await self.create_notification(
            user_id=user_id,
            title="Order Confirmed",
            message=f"Your order #{order_number} has been confirmed and will be shipped soon.",
            notification_type=NotificationType.ORDER_UPDATE,
            related_id=order_id,
            action_url=f"/orders/{order_id}"
        )

    async def notify_order_shipped(self, user_id: UUID, order_id: UUID, order_number: str) -> Notification:
        """Create notification for order shipment."""
        return await self.create_notification(
            user_id=user_id,
            title="Order Shipped",
            message=f"Your order #{order_number} has been shipped and is on its way!",
            notification_type=NotificationType.ORDER_UPDATE,
            related_id=order_id,
            action_url=f"/orders/{order_id}/tracking"
        )

    async def notify_order_delivered(self, user_id: UUID, order_id: UUID, order_number: str) -> Notification:
        """Create notification for order delivery."""
        return await self.create_notification(
            user_id=user_id,
            title="Order Delivered",
            message=f"Your order #{order_number} has been delivered. Enjoy your purchase!",
            notification_type=NotificationType.ORDER_UPDATE,
            related_id=order_id,
            action_url=f"/orders/{order_id}"
        )

    async def notify_payment_success(self, user_id: UUID, order_id: UUID, amount: float) -> Notification:
        """Create notification for successful payment."""
        return await self.create_notification(
            user_id=user_id,
            title="Payment Successful",
            message=f"Payment of ₹{amount:.2f} received successfully.",
            notification_type=NotificationType.PAYMENT,
            related_id=order_id,
            action_url=f"/orders/{order_id}"
        )

    async def notify_payment_failed(self, user_id: UUID, order_id: UUID, amount: float) -> Notification:
        """Create notification for failed payment."""
        return await self.create_notification(
            user_id=user_id,
            title="Payment Failed",
            message=f"Payment of ₹{amount:.2f} failed. Please try again.",
            notification_type=NotificationType.PAYMENT,
            related_id=order_id,
            action_url=f"/orders/{order_id}/payment"
        )

    async def notify_refund_initiated(self, user_id: UUID, order_id: UUID, amount: float) -> Notification:
        """Create notification for refund initiation."""
        return await self.create_notification(
            user_id=user_id,
            title="Refund Initiated",
            message=f"Refund of ₹{amount:.2f} has been initiated. It will be credited within 5-7 business days.",
            notification_type=NotificationType.PAYMENT,
            related_id=order_id,
            action_url=f"/orders/{order_id}"
        )

    async def notify_promotion(self, user_id: UUID, title: str, message: str, promo_url: Optional[str] = None) -> Notification:
        """Create promotional notification."""
        return await self.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=NotificationType.PROMOTION,
            action_url=promo_url
        )
