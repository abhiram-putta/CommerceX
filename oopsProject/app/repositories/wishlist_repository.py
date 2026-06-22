"""
Wishlist repository for database operations.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.base_classes import BaseRepository
from app.models.wishlist import Wishlist


class WishlistRepository(BaseRepository[Wishlist]):
    """Repository for wishlist operations."""

    def __init__(self, db: AsyncSession):
        """Initialize wishlist repository."""
        super().__init__(Wishlist, db)

    async def get_user_wishlist(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Wishlist]:
        """
        Get all wishlist items for a user.

        Args:
            user_id: User UUID
            skip: Skip N records
            limit: Limit results

        Returns:
            List of wishlist items with products
        """
        query = select(Wishlist).where(Wishlist.user_id == user_id).options(
            selectinload(Wishlist.product)
        ).order_by(Wishlist.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_wishlist_item(
        self,
        user_id: UUID,
        product_id: UUID
    ) -> Optional[Wishlist]:
        """
        Get specific wishlist item.

        Args:
            user_id: User UUID
            product_id: Product UUID

        Returns:
            Wishlist item or None
        """
        query = select(Wishlist).where(
            and_(
                Wishlist.user_id == user_id,
                Wishlist.product_id == product_id
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def is_in_wishlist(
        self,
        user_id: UUID,
        product_id: UUID
    ) -> bool:
        """
        Check if product is in user's wishlist.

        Args:
            user_id: User UUID
            product_id: Product UUID

        Returns:
            True if in wishlist
        """
        item = await self.get_wishlist_item(user_id, product_id)
        return item is not None

    async def count_wishlist_items(self, user_id: UUID) -> int:
        """
        Count items in user's wishlist.

        Args:
            user_id: User UUID

        Returns:
            Number of items
        """
        from sqlalchemy import func

        query = select(func.count(Wishlist.id)).where(Wishlist.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalar() or 0
