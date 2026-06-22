"""
Full-text search service using PostgreSQL tsvector.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SearchService:
    """Service for full-text search operations."""

    def __init__(self, product_repository: ProductRepository):
        self.product_repo = product_repository
        self.db = product_repository.db

    async def search_products(
        self,
        query: str,
        category_id: Optional[UUID] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        brand: Optional[str] = None,
        is_local: Optional[bool] = None,
        in_stock: bool = True,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Product], int]:
        """
        Full-text search for products using PostgreSQL tsvector.

        Args:
            query: Search query
            category_id: Filter by category
            min_price: Minimum price
            max_price: Maximum price
            brand: Filter by brand
            is_local: Filter by local products
            in_stock: Only show in-stock products
            skip: Offset for pagination
            limit: Limit results

        Returns:
            Tuple of (products list, total count)
        """
        if not query or not query.strip():
            return await self._get_all_products(
                category_id, min_price, max_price, brand, is_local, in_stock, skip, limit
            )

        # Build the full-text search query
        search_query = self._build_search_query(query)

        # Create tsvector for search (weighted by importance)
        # Weight: A (name) > B (description) > C (brand) > D (tags)
        tsvector_expr = func.setweight(func.to_tsvector('english', Product.name), 'A') + \
                       func.setweight(func.to_tsvector('english', func.coalesce(Product.short_description, '')), 'B') + \
                       func.setweight(func.to_tsvector('english', func.coalesce(Product.brand, '')), 'C')

        # Create tsquery
        tsquery_expr = func.to_tsquery('english', search_query)

        # Build base conditions
        conditions = [
            Product.is_active == True,
            tsvector_expr.op('@@')(tsquery_expr)
        ]

        # Add filters
        if category_id:
            conditions.append(Product.category_id == category_id)
        if min_price is not None:
            conditions.append(Product.base_price >= min_price)
        if max_price is not None:
            conditions.append(Product.base_price <= max_price)
        if brand:
            conditions.append(Product.brand.ilike(f"%{brand}%"))
        if is_local is not None:
            conditions.append(Product.is_local_product == is_local)

        # Calculate rank for ordering
        rank_expr = func.ts_rank(tsvector_expr, tsquery_expr)

        # Build query with ranking
        products_query = (
            select(Product)
            .where(and_(*conditions))
            .order_by(rank_expr.desc(), Product.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        # Get total count
        count_query = select(func.count(Product.id)).where(and_(*conditions))

        # Execute queries
        products_result = await self.db.execute(products_query)
        count_result = await self.db.execute(count_query)

        products = list(products_result.scalars().all())
        total = count_result.scalar() or 0

        logger.info(f"Full-text search for '{query}' returned {len(products)} of {total} results")
        return products, total

    async def autocomplete(
        self,
        query: str,
        limit: int = 10,
    ) -> List[str]:
        """
        Get autocomplete suggestions for search query.

        Args:
            query: Partial search query
            limit: Maximum suggestions

        Returns:
            List of suggested search terms
        """
        if not query or len(query) < 2:
            return []

        # Search for product names that match
        suggestions_query = (
            select(Product.name)
            .where(
                and_(
                    Product.is_active == True,
                    Product.name.ilike(f"%{query}%")
                )
            )
            .distinct()
            .limit(limit)
        )

        result = await self.db.execute(suggestions_query)
        suggestions = [row[0] for row in result.all()]

        return suggestions

    async def get_popular_searches(self, limit: int = 10) -> List[str]:
        """
        Get popular search terms.

        Args:
            limit: Maximum results

        Returns:
            List of popular search terms
        """
        # This would typically query a search_analytics table
        # For now, return most viewed products
        query = (
            select(Product.name)
            .where(Product.is_active == True)
            .order_by(Product.view_count.desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        return [row[0] for row in result.all()]

    async def search_suggest(
        self,
        query: str,
        limit: int = 5,
    ) -> dict:
        """
        Get search suggestions with categories.

        Args:
            query: Search query
            limit: Max suggestions per category

        Returns:
            Dictionary with categorized suggestions
        """
        if not query or len(query) < 2:
            return {
                "products": [],
                "brands": [],
                "categories": [],
            }

        # Product name suggestions
        product_query = (
            select(Product.name)
            .where(
                and_(
                    Product.is_active == True,
                    Product.name.ilike(f"%{query}%")
                )
            )
            .distinct()
            .limit(limit)
        )

        # Brand suggestions
        brand_query = (
            select(Product.brand)
            .where(
                and_(
                    Product.is_active == True,
                    Product.brand.isnot(None),
                    Product.brand.ilike(f"%{query}%")
                )
            )
            .distinct()
            .limit(limit)
        )

        # Execute queries
        product_result = await self.db.execute(product_query)
        brand_result = await self.db.execute(brand_query)

        return {
            "products": [row[0] for row in product_result.all()],
            "brands": [row[0] for row in brand_result.all()],
            "categories": [],  # Would query categories table
        }

    def _build_search_query(self, query: str) -> str:
        """
        Build tsquery string from user query.

        Handles:
        - Multiple words (AND operation)
        - Quoted phrases
        - Special characters

        Args:
            query: User search query

        Returns:
            Formatted tsquery string
        """
        # Remove special characters except spaces and quotes
        cleaned = query.strip()

        # Handle quoted phrases
        if '"' in cleaned:
            # Keep quoted phrases as-is, split others
            parts = []
            in_quote = False
            current = ""

            for char in cleaned:
                if char == '"':
                    if in_quote:
                        parts.append(f"'{current.strip()}'")
                        current = ""
                    in_quote = not in_quote
                elif in_quote:
                    current += char
                elif char.isspace():
                    if current:
                        parts.append(current)
                        current = ""
                else:
                    current += char

            if current:
                parts.append(current)

            return " & ".join(parts)

        # Simple case: split by spaces and join with AND
        words = cleaned.split()
        if not words:
            return ""

        # Add prefix matching for each word
        formatted_words = [f"{word}:*" for word in words]
        return " & ".join(formatted_words)

    async def _get_all_products(
        self,
        category_id: Optional[UUID],
        min_price: Optional[float],
        max_price: Optional[float],
        brand: Optional[str],
        is_local: Optional[bool],
        in_stock: bool,
        skip: int,
        limit: int,
    ) -> tuple[List[Product], int]:
        """Get products without search query (fallback)."""
        conditions = [Product.is_active == True]

        if category_id:
            conditions.append(Product.category_id == category_id)
        if min_price is not None:
            conditions.append(Product.base_price >= min_price)
        if max_price is not None:
            conditions.append(Product.base_price <= max_price)
        if brand:
            conditions.append(Product.brand.ilike(f"%{brand}%"))
        if is_local is not None:
            conditions.append(Product.is_local_product == is_local)

        # Query products
        products_query = (
            select(Product)
            .where(and_(*conditions))
            .order_by(Product.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        # Count query
        count_query = select(func.count(Product.id)).where(and_(*conditions))

        products_result = await self.db.execute(products_query)
        count_result = await self.db.execute(count_query)

        products = list(products_result.scalars().all())
        total = count_result.scalar() or 0

        return products, total
