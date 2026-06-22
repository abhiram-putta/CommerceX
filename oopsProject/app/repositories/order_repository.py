"""
Order repository for database operations.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.base_classes import BaseRepository
from app.models.order import Order, OrderItem, OrderTracking
from app.utils.enums import OrderStatus


class OrderRepository(BaseRepository[Order]):
    """Repository for order operations."""

    def __init__(self, db: AsyncSession):
        """Initialize order repository."""
        super().__init__(Order, db)

    async def get_with_items(self, order_id: UUID) -> Optional[Order]:
        """
        Get order with items and tracking.

        Args:
            order_id: Order UUID

        Returns:
            Order with relationships loaded
        """
        query = select(Order).where(Order.id == order_id).options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.tracking_history),
            selectinload(Order.customer)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_order_number(self, order_number: str) -> Optional[Order]:
        """
        Get order by order number.

        Args:
            order_number: Order number string

        Returns:
            Order instance or None
        """
        query = select(Order).where(Order.order_number == order_number)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_orders(
        self,
        user_id: UUID,
        status: Optional[OrderStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """
        Get orders for a user.

        Args:
            user_id: User UUID
            status: Optional status filter
            skip: Skip N records
            limit: Limit results

        Returns:
            List of orders
        """
        query = select(Order).where(Order.customer_id == user_id)

        if status:
            query = query.where(Order.status == status)

        query = query.options(
            selectinload(Order.items).selectinload(OrderItem.product)
        ).order_by(Order.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_retailer_orders(
        self,
        retailer_id: UUID,
        status: Optional[OrderStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """
        Get orders for a retailer.

        Args:
            retailer_id: Retailer UUID
            status: Optional status filter
            skip: Skip N records
            limit: Limit results

        Returns:
            List of orders
        """
        query = select(Order).where(Order.retailer_id == retailer_id)

        if status:
            query = query.where(Order.status == status)

        query = query.options(
            selectinload(Order.items).selectinload(OrderItem.product),
            selectinload(Order.customer)
        ).order_by(Order.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_status(
        self,
        order_id: UUID,
        new_status: OrderStatus
    ) -> Optional[Order]:
        """
        Update order status.

        Args:
            order_id: Order UUID
            new_status: New status

        Returns:
            Updated order or None
        """
        order = await self.get(order_id)
        if not order:
            return None

        order.status = new_status
        await self.db.commit()
        await self.db.refresh(order)

        return order


class OrderItemRepository(BaseRepository[OrderItem]):
    """Repository for order item operations."""

    def __init__(self, db: AsyncSession):
        """Initialize order item repository."""
        super().__init__(OrderItem, db)

    async def get_by_order(self, order_id: UUID) -> List[OrderItem]:
        """
        Get all items for an order.

        Args:
            order_id: Order UUID

        Returns:
            List of order items
        """
        query = select(OrderItem).where(OrderItem.order_id == order_id).options(
            selectinload(OrderItem.product)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())


class OrderTrackingRepository(BaseRepository[OrderTracking]):
    """Repository for order tracking operations."""

    def __init__(self, db: AsyncSession):
        """Initialize order tracking repository."""
        super().__init__(OrderTracking, db)

    async def get_by_order(self, order_id: UUID) -> List[OrderTracking]:
        """
        Get tracking history for an order.

        Args:
            order_id: Order UUID

        Returns:
            List of tracking entries
        """
        query = select(OrderTracking).where(
            OrderTracking.order_id == order_id
        ).order_by(OrderTracking.timestamp.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def add_tracking_update(
        self,
        order_id: UUID,
        status: OrderStatus,
        location: Optional[str] = None,
        notes: Optional[str] = None
    ) -> OrderTracking:
        """
        Add tracking update for an order.

        Args:
            order_id: Order UUID
            status: Current status
            location: Optional location
            notes: Optional notes

        Returns:
            Created tracking entry
        """
        tracking_data = {
            'order_id': order_id,
            'status': status,
            'location': location,
            'notes': notes
        }

        tracking = await self.create(tracking_data)
        return tracking
