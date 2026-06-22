"""
Category repository for category-specific database operations.
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.category import Category
from app.repositories.base_repository import CRUDRepository


class CategoryRepository(CRUDRepository[Category]):
    """Category repository with custom methods."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize category repository.

        Args:
            db: Database session
        """
        super().__init__(Category, db)

    async def get_by_slug(self, slug: str) -> Optional[Category]:
        """
        Get category by slug.

        Args:
            slug: Category slug

        Returns:
            Category instance or None
        """
        result = await self.db.execute(
            select(Category)
            .where(Category.slug == slug)
            .options(selectinload(Category.subcategories))
        )
        return result.scalar_one_or_none()

    async def get_root_categories(self) -> List[Category]:
        """Get all root categories (no parent)."""
        result = await self.db.execute(
            select(Category)
            .where(Category.parent_id == None, Category.is_active == True)
            .order_by(Category.display_order)
        )
        return list(result.scalars().all())

    async def get_subcategories(self, parent_id: str) -> List[Category]:
        """Get subcategories of a parent category."""
        result = await self.db.execute(
            select(Category)
            .where(Category.parent_id == parent_id, Category.is_active == True)
            .order_by(Category.display_order)
        )
        return list(result.scalars().all())

    async def get_featured(self) -> List[Category]:
        """Get featured categories."""
        result = await self.db.execute(
            select(Category)
            .where(Category.is_featured == True, Category.is_active == True)
            .order_by(Category.display_order)
        )
        return list(result.scalars().all())
