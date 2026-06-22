"""
Repository for coupon data access.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_classes import BaseRepository
from app.models.coupon import Coupon, CouponUsage


class CouponRepository(BaseRepository[Coupon]):
    """Repository for coupon operations."""

    async def get_by_code(self, code: str) -> Optional[Coupon]:
        """
        Get coupon by code.

        Args:
            code: Coupon code

        Returns:
            Coupon instance or None
        """
        query = select(Coupon).where(
            and_(
                Coupon.code == code.upper(),
                Coupon.is_active == True
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_valid_coupons(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Coupon]:
        """
        Get all currently valid coupons.

        Args:
            skip: Skip N records
            limit: Limit results

        Returns:
            List of valid coupons
        """
        now = datetime.utcnow()
        query = (
            select(Coupon)
            .where(
                and_(
                    Coupon.is_active == True,
                    Coupon.valid_from <= now,
                    Coupon.valid_until >= now,
                    or_(
                        Coupon.usage_limit.is_(None),
                        Coupon.used_count < Coupon.usage_limit
                    )
                )
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def increment_usage(self, coupon_id: UUID) -> None:
        """
        Increment coupon usage count.

        Args:
            coupon_id: Coupon UUID
        """
        coupon = await self.get(coupon_id)
        if coupon:
            coupon.used_count += 1
            await self.db.commit()


class CouponUsageRepository(BaseRepository[CouponUsage]):
    """Repository for coupon usage tracking."""

    async def get_user_usage_count(
        self,
        coupon_id: UUID,
        user_id: UUID
    ) -> int:
        """
        Get number of times user has used a coupon.

        Args:
            coupon_id: Coupon UUID
            user_id: User UUID

        Returns:
            Usage count
        """
        query = select(CouponUsage).where(
            and_(
                CouponUsage.coupon_id == coupon_id,
                CouponUsage.user_id == user_id
            )
        )
        result = await self.db.execute(query)
        return len(list(result.scalars().all()))

    async def get_user_coupon_history(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[CouponUsage]:
        """
        Get user's coupon usage history.

        Args:
            user_id: User UUID
            skip: Skip N records
            limit: Limit results

        Returns:
            List of coupon usages
        """
        query = (
            select(CouponUsage)
            .where(CouponUsage.user_id == user_id)
            .order_by(CouponUsage.used_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
