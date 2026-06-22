"""
Inventory repository for database operations.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_classes import BaseRepository
from app.models.inventory import Inventory


class InventoryRepository(BaseRepository[Inventory]):
    """Repository for inventory operations."""

    def __init__(self, db: AsyncSession):
        """Initialize inventory repository."""
        super().__init__(Inventory, db)

    async def get_by_product_and_owner(
        self,
        product_id: UUID,
        owner_id: UUID
    ) -> Optional[Inventory]:
        """
        Get inventory by product and owner.

        Args:
            product_id: Product UUID
            owner_id: Owner (retailer/wholesaler) UUID

        Returns:
            Inventory instance or None
        """
        query = select(Inventory).where(
            and_(
                Inventory.product_id == product_id,
                Inventory.owner_id == owner_id
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_product(
        self,
        product_id: UUID,
        available_only: bool = True
    ) -> List[Inventory]:
        """
        Get all inventory entries for a product.

        Args:
            product_id: Product UUID
            available_only: Only return items with stock > 0

        Returns:
            List of inventory entries
        """
        query = select(Inventory).where(Inventory.product_id == product_id)

        if available_only:
            query = query.where(Inventory.stock_quantity > 0)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_owner(
        self,
        owner_id: UUID,
        available_only: bool = False
    ) -> List[Inventory]:
        """
        Get all inventory for an owner (retailer/wholesaler).

        Args:
            owner_id: Owner UUID
            available_only: Only return items with stock > 0

        Returns:
            List of inventory entries
        """
        query = select(Inventory).where(Inventory.owner_id == owner_id)

        if available_only:
            query = query.where(Inventory.stock_quantity > 0)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_stock(
        self,
        inventory_id: UUID,
        quantity_change: int
    ) -> Optional[Inventory]:
        """
        Update inventory stock quantity.

        Args:
            inventory_id: Inventory UUID
            quantity_change: Amount to change (positive or negative)

        Returns:
            Updated inventory or None
        """
        inventory = await self.get(inventory_id)
        if not inventory:
            return None

        inventory.stock_quantity += quantity_change

        # Ensure stock doesn't go negative
        if inventory.stock_quantity < 0:
            inventory.stock_quantity = 0

        await self.db.commit()
        await self.db.refresh(inventory)

        return inventory

    async def check_availability(
        self,
        inventory_id: UUID,
        required_quantity: int
    ) -> bool:
        """
        Check if enough stock is available.

        Args:
            inventory_id: Inventory UUID
            required_quantity: Required quantity

        Returns:
            True if available
        """
        inventory = await self.get(inventory_id)
        if not inventory:
            return False

        return inventory.stock_quantity >= required_quantity
