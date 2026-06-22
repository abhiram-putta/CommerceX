"""
Coupon service for discount code management.
"""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.coupon import Coupon, CouponUsage
from app.repositories.coupon_repository import CouponRepository, CouponUsageRepository
from app.repositories.order_repository import OrderRepository
from app.utils.enums import CouponType, DiscountType
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CouponService:
    """Service for coupon operations."""

    def __init__(
        self,
        coupon_repository: CouponRepository,
        usage_repository: CouponUsageRepository,
        order_repository: OrderRepository,
    ):
        self.coupon_repository = coupon_repository
        self.usage_repository = usage_repository
        self.order_repository = order_repository

    async def validate_and_apply_coupon(
        self,
        code: str,
        user_id: UUID,
        order_amount: float,
        product_ids: Optional[List[UUID]] = None,
        category_ids: Optional[List[UUID]] = None,
    ) -> Dict:
        """
        Validate coupon and calculate discount.

        Args:
            code: Coupon code
            user_id: User UUID
            order_amount: Order amount before discount
            product_ids: List of product IDs in order
            category_ids: List of category IDs in order

        Returns:
            Dict with discount details

        Raises:
            NotFoundError: If coupon not found
            BadRequestError: If coupon is not valid
        """
        # Get coupon
        coupon = await self.coupon_repository.get_by_code(code.upper())
        if not coupon:
            raise NotFoundError("Coupon not found")

        # Check if coupon is valid
        if not coupon.is_valid():
            raise BadRequestError("Coupon is not currently valid")

        # Check validity period
        now = datetime.utcnow()
        if not (coupon.valid_from <= now <= coupon.valid_until):
            raise BadRequestError("Coupon has expired")

        # Check minimum order amount
        if coupon.minimum_order_amount and order_amount < coupon.minimum_order_amount:
            raise BadRequestError(
                f"Minimum order amount of ₹{coupon.minimum_order_amount} required"
            )

        # Check maximum order amount
        if coupon.maximum_order_amount and order_amount > coupon.maximum_order_amount:
            raise BadRequestError(
                f"Maximum order amount of ₹{coupon.maximum_order_amount} exceeded"
            )

        # Check user-specific restrictions
        if coupon.applicable_users and str(user_id) not in coupon.applicable_users:
            raise BadRequestError("This coupon is not available for your account")

        # Check first-time user restriction
        if coupon.first_time_users_only:
            user_orders = await self.order_repository.get_user_orders(user_id)
            if len(user_orders) > 0:
                raise BadRequestError("This coupon is only for first-time users")

        # Check usage limit per user
        user_usage_count = await self.usage_repository.get_user_usage_count(
            coupon.id, user_id
        )
        if not coupon.can_user_use(user_usage_count):
            raise BadRequestError("You have already used this coupon maximum times")

        # Check product/category restrictions
        if coupon.applicable_products and product_ids:
            if not any(str(pid) in coupon.applicable_products for pid in product_ids):
                raise BadRequestError("This coupon is not applicable to your cart items")

        if coupon.applicable_categories and category_ids:
            if not any(str(cid) in coupon.applicable_categories for cid in category_ids):
                raise BadRequestError("This coupon is not applicable to your cart items")

        # Calculate discount
        discount_amount = self._calculate_discount(coupon, order_amount)

        return {
            "coupon_id": coupon.id,
            "code": coupon.code,
            "discount_type": coupon.discount_type,
            "discount_value": coupon.discount_value,
            "discount_amount": discount_amount,
            "final_amount": order_amount - discount_amount,
            "message": f"Coupon applied! You saved ₹{discount_amount:.2f}",
        }

    def _calculate_discount(self, coupon: Coupon, order_amount: float) -> float:
        """
        Calculate discount amount.

        Args:
            coupon: Coupon instance
            order_amount: Order amount

        Returns:
            Discount amount
        """
        if coupon.discount_type == DiscountType.PERCENTAGE:
            discount = order_amount * (coupon.discount_value / 100)
            # Apply max discount cap if set
            if coupon.max_discount_amount:
                discount = min(discount, coupon.max_discount_amount)
        else:  # FIXED_AMOUNT
            discount = min(coupon.discount_value, order_amount)

        return round(discount, 2)

    async def record_usage(
        self,
        coupon_id: UUID,
        user_id: UUID,
        order_id: UUID,
        discount_amount: float,
        order_amount: float,
    ) -> CouponUsage:
        """
        Record coupon usage.

        Args:
            coupon_id: Coupon UUID
            user_id: User UUID
            order_id: Order UUID
            discount_amount: Discount amount applied
            order_amount: Order amount before discount

        Returns:
            CouponUsage instance
        """
        # Create usage record
        usage = await self.usage_repository.create({
            "coupon_id": coupon_id,
            "user_id": user_id,
            "order_id": order_id,
            "discount_amount": discount_amount,
            "order_amount": order_amount,
        })

        # Increment coupon usage count
        await self.coupon_repository.increment_usage(coupon_id)

        logger.info(f"Coupon {coupon_id} used by user {user_id}")
        return usage

    async def get_available_coupons(
        self,
        user_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Coupon]:
        """
        Get available coupons for user.

        Args:
            user_id: User UUID (optional)
            skip: Skip N records
            limit: Limit results

        Returns:
            List of available coupons
        """
        coupons = await self.coupon_repository.get_valid_coupons(skip, limit)

        # Filter user-specific coupons if user_id provided
        if user_id:
            filtered_coupons = []
            for coupon in coupons:
                # Skip if coupon is for specific users and this user is not in the list
                if coupon.applicable_users and str(user_id) not in coupon.applicable_users:
                    continue

                # Check first-time user restriction
                if coupon.first_time_users_only:
                    user_orders = await self.order_repository.get_user_orders(user_id)
                    if len(user_orders) > 0:
                        continue

                # Check usage limit per user
                user_usage_count = await self.usage_repository.get_user_usage_count(
                    coupon.id, user_id
                )
                if not coupon.can_user_use(user_usage_count):
                    continue

                filtered_coupons.append(coupon)

            return filtered_coupons

        return coupons

    async def create_coupon(self, coupon_data: dict) -> Coupon:
        """
        Create a new coupon.

        Args:
            coupon_data: Coupon creation data

        Returns:
            Created coupon
        """
        # Ensure code is uppercase
        if "code" in coupon_data:
            coupon_data["code"] = coupon_data["code"].upper()

        # Check if code already exists
        existing = await self.coupon_repository.get_by_code(coupon_data["code"])
        if existing:
            raise BadRequestError("Coupon code already exists")

        coupon = await self.coupon_repository.create(coupon_data)
        logger.info(f"Coupon created: {coupon.code}")
        return coupon

    async def update_coupon(self, coupon_id: UUID, update_data: dict) -> Coupon:
        """
        Update coupon.

        Args:
            coupon_id: Coupon UUID
            update_data: Update data

        Returns:
            Updated coupon
        """
        coupon = await self.coupon_repository.update(coupon_id, update_data)
        if not coupon:
            raise NotFoundError("Coupon not found")

        logger.info(f"Coupon updated: {coupon.code}")
        return coupon

    async def deactivate_coupon(self, coupon_id: UUID) -> Coupon:
        """
        Deactivate a coupon.

        Args:
            coupon_id: Coupon UUID

        Returns:
            Deactivated coupon
        """
        return await self.update_coupon(coupon_id, {"is_active": False})

    async def get_user_coupon_history(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
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
        return await self.usage_repository.get_user_coupon_history(user_id, skip, limit)
