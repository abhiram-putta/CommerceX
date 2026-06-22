"""
Cart repository for database operations.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.base_classes import BaseRepository
from app.models.cart import Cart


class CartRepository(BaseRepository[Cart]):
    """Repository for cart (cart item) operations."""

    def __init__(self, db: AsyncSession):
        """Initialize cart repository."""
        super().__init__(Cart, db)

    async def get_user_cart_items(
        self,
        user_id: UUID,
        include_product: bool = True,
        active_only: bool = True
    ) -> List[Cart]:
        """
        Get all cart items for a user.

        Args:
            user_id: User UUID
            include_product: Whether to include product details
            active_only: Only return active cart items

        Returns:
            List of cart items
        """
        query = select(Cart).where(Cart.user_id == user_id)

        if active_only:
            query = query.where(Cart.is_active == True)

        if include_product:
            query = query.options(
                selectinload(Cart.product),
                selectinload(Cart.inventory)
            )

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_cart_item(
        self,
        user_id: UUID,
        product_id: UUID,
        inventory_id: Optional[UUID] = None
    ) -> Optional[Cart]:
        """
        Get specific cart item by user and product.

        Args:
            user_id: User UUID
            product_id: Product UUID
            inventory_id: Optional inventory UUID

        Returns:
            Cart item or None
        """
        query = select(Cart).where(
            and_(
                Cart.user_id == user_id,
                Cart.product_id == product_id,
                Cart.is_active == True
            )
        )

        if inventory_id:
            query = query.where(Cart.inventory_id == inventory_id)

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update_quantity(
        self,
        cart_item_id: UUID,
        quantity: int
    ) -> Optional[Cart]:
        """
        Update cart item quantity.

        Args:
            cart_item_id: Cart item UUID
            quantity: New quantity

        Returns:
            Updated cart item or None
        """
        cart_item = await self.get(cart_item_id)
        if not cart_item:
            return None

        cart_item.quantity = quantity
        await self.db.commit()
        await self.db.refresh(cart_item)

        return cart_item

    async def remove_item(self, cart_item_id: UUID) -> bool:
        """
        Remove (deactivate) item from cart.

        Args:
            cart_item_id: Cart item UUID

        Returns:
            True if successful
        """
        cart_item = await self.get(cart_item_id)
        if not cart_item:
            return False

        cart_item.is_active = False
        await self.db.commit()
        return True

    async def clear_user_cart(self, user_id: UUID) -> bool:
        """
        Remove all items from user's cart.

        Args:
            user_id: User UUID

        Returns:
            True if successful
        """
        cart_items = await self.get_user_cart_items(user_id, include_product=False)

        for item in cart_items:
            item.is_active = False

        await self.db.commit()
        return True

    async def get_cart_total(self, user_id: UUID) -> float:
        """
        Calculate total value of user's cart.

        Args:
            user_id: User UUID

        Returns:
            Total cart value
        """
        cart_items = await self.get_user_cart_items(user_id, include_product=False)
        return sum(item.subtotal for item in cart_items)
