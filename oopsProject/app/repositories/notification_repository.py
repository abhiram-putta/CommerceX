"""
Notification repository for database operations.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_classes import BaseRepository
from app.models.notification import Notification
from app.utils.enums import NotificationType


class NotificationRepository(BaseRepository[Notification]):
    """Repository for notification operations."""

    def __init__(self, db: AsyncSession):
        """Initialize notification repository."""
        super().__init__(Notification, db)

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
        query = select(Notification).where(Notification.user_id == user_id)

        if unread_only:
            query = query.where(Notification.is_read == False)

        if notification_type:
            query = query.where(Notification.notification_type == notification_type)

        query = query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def mark_as_read(self, notification_id: UUID) -> Optional[Notification]:
        """
        Mark notification as read.

        Args:
            notification_id: Notification UUID

        Returns:
            Updated notification or None
        """
        notification = await self.get(notification_id)
        if not notification:
            return None

        notification.is_read = True
        await self.db.commit()
        await self.db.refresh(notification)

        return notification

    async def mark_all_as_read(self, user_id: UUID) -> int:
        """
        Mark all user notifications as read.

        Args:
            user_id: User UUID

        Returns:
            Number of notifications updated
        """
        from sqlalchemy import update

        stmt = (
            update(Notification)
            .where(
                and_(
                    Notification.user_id == user_id,
                    Notification.is_read == False
                )
            )
            .values(is_read=True)
        )

        result = await self.db.execute(stmt)
        await self.db.commit()

        return result.rowcount

    async def get_unread_count(self, user_id: UUID) -> int:
        """
        Get count of unread notifications.

        Args:
            user_id: User UUID

        Returns:
            Unread notification count
        """
        from sqlalchemy import func

        query = select(func.count(Notification.id)).where(
            and_(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
        )

        result = await self.db.execute(query)
        return result.scalar() or 0

    async def delete_user_notifications(
        self,
        user_id: UUID,
        notification_ids: Optional[List[UUID]] = None
    ) -> int:
        """
        Delete user notifications.

        Args:
            user_id: User UUID
            notification_ids: Optional list of specific notification IDs

        Returns:
            Number of notifications deleted
        """
        query = select(Notification).where(Notification.user_id == user_id)

        if notification_ids:
            query = query.where(Notification.id.in_(notification_ids))

        result = await self.db.execute(query)
        notifications = result.scalars().all()

        count = 0
        for notification in notifications:
            await self.db.delete(notification)
            count += 1

        await self.db.commit()
        return count
