"""
Review repository for database operations.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.base_classes import BaseRepository
from app.models.review import Review


class ReviewRepository(BaseRepository[Review]):
    """Repository for review operations."""

    def __init__(self, db: AsyncSession):
        """Initialize review repository."""
        super().__init__(Review, db)

    async def get_product_reviews(
        self,
        product_id: UUID,
        verified_only: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[Review]:
        """
        Get reviews for a product.

        Args:
            product_id: Product UUID
            verified_only: Only return verified purchase reviews
            skip: Skip N records
            limit: Limit results

        Returns:
            List of reviews
        """
        query = select(Review).where(Review.product_id == product_id)

        if verified_only:
            query = query.where(Review.is_verified_purchase == True)

        query = query.options(
            selectinload(Review.user)
        ).order_by(Review.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_user_reviews(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Review]:
        """
        Get reviews by a user.

        Args:
            user_id: User UUID
            skip: Skip N records
            limit: Limit results

        Returns:
            List of reviews
        """
        query = select(Review).where(Review.user_id == user_id).options(
            selectinload(Review.product)
        ).order_by(Review.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_user_product_review(
        self,
        user_id: UUID,
        product_id: UUID
    ) -> Optional[Review]:
        """
        Get user's review for a specific product.

        Args:
            user_id: User UUID
            product_id: Product UUID

        Returns:
            Review or None
        """
        query = select(Review).where(
            and_(
                Review.user_id == user_id,
                Review.product_id == product_id
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_average_rating(self, product_id: UUID) -> Optional[float]:
        """
        Get average rating for a product.

        Args:
            product_id: Product UUID

        Returns:
            Average rating or None
        """
        query = select(func.avg(Review.rating)).where(
            Review.product_id == product_id
        )
        result = await self.db.execute(query)
        avg_rating = result.scalar()

        return float(avg_rating) if avg_rating else None

    async def get_rating_counts(self, product_id: UUID) -> dict:
        """
        Get count of reviews for each rating (1-5 stars).

        Args:
            product_id: Product UUID

        Returns:
            Dict with rating counts {1: count, 2: count, ...}
        """
        query = select(
            Review.rating,
            func.count(Review.id)
        ).where(
            Review.product_id == product_id
        ).group_by(Review.rating)

        result = await self.db.execute(query)
        rows = result.all()

        # Initialize all ratings to 0
        rating_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}

        # Update with actual counts
        for rating, count in rows:
            rating_counts[rating] = count

        return rating_counts

    async def count_product_reviews(self, product_id: UUID) -> int:
        """
        Count total reviews for a product.

        Args:
            product_id: Product UUID

        Returns:
            Review count
        """
        query = select(func.count(Review.id)).where(
            Review.product_id == product_id
        )
        result = await self.db.execute(query)
        return result.scalar() or 0
