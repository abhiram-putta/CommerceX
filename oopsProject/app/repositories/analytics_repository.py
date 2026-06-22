"""
Repository for analytics data access.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_classes import BaseRepository
from app.models.analytics import SearchQuery


class AnalyticsRepository(BaseRepository[SearchQuery]):
    """Repository for analytics operations."""

    async def get_recent_searches(self, limit: int = 100) -> List[SearchQuery]:
        """
        Get recent search queries.

        Args:
            limit: Number of results

        Returns:
            List of search queries
        """
        query = (
            select(SearchQuery)
            .order_by(SearchQuery.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_popular_searches(self, limit: int = 10) -> List[dict]:
        """
        Get most popular search queries.

        Args:
            limit: Number of results

        Returns:
            List of search queries with counts
        """
        # Simplified version - returns empty for now
        # TODO: Implement proper aggregation
        return []
