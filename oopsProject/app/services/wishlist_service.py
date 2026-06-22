"""
Wishlist service for wishlist management business logic.
"""
from typing import List
from uuid import UUID

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.wishlist import Wishlist
from app.repositories.product_repository import ProductRepository
from app.repositories.wishlist_repository import WishlistRepository
from app.utils.logger import get_logger

logger = get_logger(__name__)


class WishlistService:
    """Wishlist service with business logic."""

    def __init__(
        self,
        wishlist_repository: WishlistRepository,
        product_repository: ProductRepository
    ):
        """
        Initialize wishlist service.

        Args:
            wishlist_repository: Wishlist repository instance
            product_repository: Product repository instance
        """
        self.wishlist_repository = wishlist_repository
        self.product_repository = product_repository

    async def add_to_wishlist(
        self,
        user_id: UUID,
        product_id: UUID
    ) -> Wishlist:
        """
        Add product to wishlist.

        Args:
            user_id: User UUID
            product_id: Product UUID

        Returns:
            Created wishlist item

        Raises:
            NotFoundError: If product not found
            BadRequestError: If already in wishlist
        """
        # Verify product exists
        product = await self.product_repository.get(product_id)
        if not product:
            raise NotFoundError("Product not found")

        # Check if already in wishlist
        existing = await self.wishlist_repository.get_wishlist_item(user_id, product_id)
        if existing:
            raise BadRequestError("Product already in wishlist")

        # Add to wishlist
        wishlist_item = await self.wishlist_repository.create({
            'user_id': user_id,
            'product_id': product_id
        })

        logger.info(f"Product {product_id} added to wishlist for user {user_id}")
        return wishlist_item

    async def remove_from_wishlist(
        self,
        user_id: UUID,
        product_id: UUID
    ) -> bool:
        """
        Remove product from wishlist.

        Args:
            user_id: User UUID
            product_id: Product UUID

        Returns:
            True if successful

        Raises:
            NotFoundError: If not in wishlist
        """
        wishlist_item = await self.wishlist_repository.get_wishlist_item(user_id, product_id)
        if not wishlist_item:
            raise NotFoundError("Product not in wishlist")

        success = await self.wishlist_repository.delete(wishlist_item.id)
        logger.info(f"Product {product_id} removed from wishlist for user {user_id}")
        return success

    async def get_user_wishlist(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Wishlist]:
        """
        Get user's wishlist.

        Args:
            user_id: User UUID
            skip: Skip N records
            limit: Limit results

        Returns:
            List of wishlist items
        """
        return await self.wishlist_repository.get_user_wishlist(user_id, skip, limit)

    async def clear_wishlist(self, user_id: UUID) -> int:
        """
        Clear all items from wishlist.

        Args:
            user_id: User UUID

        Returns:
            Number of items removed
        """
        wishlist_items = await self.wishlist_repository.get_user_wishlist(user_id, limit=1000)

        count = 0
        for item in wishlist_items:
            await self.wishlist_repository.delete(item.id)
            count += 1

        logger.info(f"Cleared {count} items from wishlist for user {user_id}")
        return count

    async def is_in_wishlist(
        self,
        user_id: UUID,
        product_id: UUID
    ) -> bool:
        """
        Check if product is in wishlist.

        Args:
            user_id: User UUID
            product_id: Product UUID

        Returns:
            True if in wishlist
        """
        return await self.wishlist_repository.is_in_wishlist(user_id, product_id)

    async def get_wishlist_count(self, user_id: UUID) -> int:
        """
        Get count of items in wishlist.

        Args:
            user_id: User UUID

        Returns:
            Number of items
        """
        return await self.wishlist_repository.count_wishlist_items(user_id)
