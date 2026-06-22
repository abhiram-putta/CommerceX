"""
Product repository for product-specific database operations.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.repositories.base_repository import CRUDRepository


class ProductRepository(CRUDRepository[Product]):
    """Product repository with custom methods."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize product repository.

        Args:
            db: Database session
        """
        super().__init__(Product, db)

    async def get_by_slug(self, slug: str) -> Optional[Product]:
        """
        Get product by slug.

        Args:
            slug: Product slug

        Returns:
            Product instance or None
        """
        result = await self.db.execute(
            select(Product)
            .where(Product.slug == slug)
            .options(selectinload(Product.category))
        )
        return result.scalar_one_or_none()

    async def search(
        self,
        query: str,
        category_id: Optional[UUID] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        brand: Optional[str] = None,
        is_local: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Product]:
        """
        Search products with filters.

        Args:
            query: Search query
            category_id: Filter by category
            min_price: Minimum price
            max_price: Maximum price
            brand: Filter by brand
            is_local: Filter local products
            skip: Records to skip
            limit: Max records

        Returns:
            List of products
        """
        stmt = select(Product).where(Product.is_active == True)

        # Text search
        if query:
            stmt = stmt.where(
                or_(
                    Product.name.ilike(f"%{query}%"),
                    Product.description.ilike(f"%{query}%"),
                    Product.brand.ilike(f"%{query}%"),
                )
            )

        # Filters
        if category_id:
            stmt = stmt.where(Product.category_id == category_id)
        if min_price is not None:
            stmt = stmt.where(Product.base_price >= min_price)
        if max_price is not None:
            stmt = stmt.where(Product.base_price <= max_price)
        if brand:
            stmt = stmt.where(Product.brand == brand)
        if is_local is not None:
            stmt = stmt.where(Product.is_local_product == is_local)

        # Pagination
        stmt = stmt.offset(skip).limit(limit)

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_featured(self, limit: int = 10) -> List[Product]:
        """Get featured products."""
        result = await self.db.execute(
            select(Product)
            .where(Product.is_featured == True, Product.is_active == True)
            .order_by(Product.view_count.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def increment_view_count(self, product_id: UUID) -> None:
        """Increment product view count."""
        product = await self.get(product_id)
        if product:
            product.view_count += 1
            self.db.add(product)
            await self.db.flush()
