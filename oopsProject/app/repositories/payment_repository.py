"""
Payment repository for database operations.
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.base_classes import BaseRepository
from app.models.payment import Payment
from app.utils.enums import PaymentStatus


class PaymentRepository(BaseRepository[Payment]):
    """Repository for payment operations."""

    def __init__(self, db: AsyncSession):
        """Initialize payment repository."""
        super().__init__(Payment, db)

    async def get_by_order(self, order_id: UUID) -> Optional[Payment]:
        """
        Get payment by order ID.

        Args:
            order_id: Order UUID

        Returns:
            Payment instance or None
        """
        query = select(Payment).where(Payment.order_id == order_id).options(
            selectinload(Payment.order)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_transaction_id(self, transaction_id: str) -> Optional[Payment]:
        """
        Get payment by transaction/payment ID from gateway.

        Args:
            transaction_id: Transaction ID from payment gateway

        Returns:
            Payment instance or None
        """
        query = select(Payment).where(Payment.transaction_id == transaction_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_razorpay_payment_id(
        self,
        razorpay_payment_id: str
    ) -> Optional[Payment]:
        """
        Get payment by Razorpay payment ID.

        Args:
            razorpay_payment_id: Razorpay payment ID

        Returns:
            Payment instance or None
        """
        query = select(Payment).where(
            Payment.razorpay_payment_id == razorpay_payment_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_user_payments(
        self,
        user_id: UUID,
        status: Optional[PaymentStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Payment]:
        """
        Get payments for a user.

        Args:
            user_id: User UUID
            status: Optional status filter
            skip: Skip N records
            limit: Limit results

        Returns:
            List of payments
        """
        query = select(Payment).where(Payment.user_id == user_id)

        if status:
            query = query.where(Payment.status == status)

        query = query.options(
            selectinload(Payment.order)
        ).order_by(Payment.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_status(
        self,
        payment_id: UUID,
        status: PaymentStatus,
        **kwargs
    ) -> Optional[Payment]:
        """
        Update payment status and related fields.

        Args:
            payment_id: Payment UUID
            status: New status
            **kwargs: Additional fields to update

        Returns:
            Updated payment or None
        """
        payment = await self.get(payment_id)
        if not payment:
            return None

        payment.status = status

        # Update additional fields
        for key, value in kwargs.items():
            if hasattr(payment, key):
                setattr(payment, key, value)

        await self.db.commit()
        await self.db.refresh(payment)

        return payment

    async def get_total_revenue(
        self,
        user_id: Optional[UUID] = None,
        status: PaymentStatus = PaymentStatus.SUCCESS
    ) -> float:
        """
        Calculate total revenue from successful payments.

        Args:
            user_id: Optional user filter
            status: Payment status filter

        Returns:
            Total revenue amount
        """
        from sqlalchemy import func

        query = select(func.sum(Payment.amount)).where(Payment.status == status)

        if user_id:
            query = query.where(Payment.user_id == user_id)

        result = await self.db.execute(query)
        total = result.scalar()

        return float(total) if total else 0.0
