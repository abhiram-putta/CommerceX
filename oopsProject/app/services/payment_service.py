"""
Payment service for payment processing with Razorpay integration.
"""
import hashlib
import hmac
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

import razorpay

from app.config.settings import get_settings
from app.core.exceptions import BadRequestError, NotFoundError
from app.models.payment import Payment
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.utils.enums import PaymentStatus, PaymentMethod, OrderStatus
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class PaymentService:
    """Payment service with Razorpay integration."""

    def __init__(
        self,
        payment_repository: PaymentRepository,
        order_repository: OrderRepository
    ):
        """
        Initialize payment service.

        Args:
            payment_repository: Payment repository instance
            order_repository: Order repository instance
        """
        self.payment_repository = payment_repository
        self.order_repository = order_repository

        # Initialize Razorpay client
        self.razorpay_client = None
        if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
            try:
                self.razorpay_client = razorpay.Client(
                    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
                )
                logger.info("Razorpay client initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Razorpay: {e}")

    async def create_razorpay_order(
        self,
        order_id: UUID,
        user_id: UUID
    ) -> Dict[str, Any]:
        """
        Create Razorpay order for payment.

        Args:
            order_id: Order UUID
            user_id: User UUID

        Returns:
            Dict with Razorpay order details

        Raises:
            NotFoundError: If order not found
            BadRequestError: If validation fails
        """
        # Get order
        order = await self.order_repository.get(order_id)
        if not order:
            raise NotFoundError("Order not found")

        # Verify ownership
        if order.customer_id != user_id:
            raise BadRequestError("Unauthorized to create payment for this order")

        # Check if payment already exists
        existing_payment = await self.payment_repository.get_by_order(order_id)
        if existing_payment and existing_payment.status == PaymentStatus.SUCCESS:
            raise BadRequestError("Order already paid")

        # Check Razorpay client
        if not self.razorpay_client:
            raise BadRequestError("Payment gateway not configured")

        try:
            # Create Razorpay order
            razorpay_order = self.razorpay_client.order.create({
                'amount': int(order.total_amount * 100),  # Convert to paise
                'currency': 'INR',
                'receipt': str(order.order_number),
                'notes': {
                    'order_id': str(order_id),
                    'customer_id': str(user_id)
                }
            })

            # Create or update payment record
            payment_data = {
                'order_id': order_id,
                'user_id': user_id,
                'amount': order.total_amount,
                'currency': 'INR',
                'payment_method': PaymentMethod.RAZORPAY,
                'status': PaymentStatus.PENDING,
                'razorpay_order_id': razorpay_order['id'],
                'metadata': {
                    'razorpay_order': razorpay_order,
                    'created_at': datetime.utcnow().isoformat()
                }
            }

            if existing_payment:
                payment = await self.payment_repository.update(
                    existing_payment.id,
                    payment_data
                )
            else:
                payment = await self.payment_repository.create(payment_data)

            logger.info(f"Razorpay order created: {razorpay_order['id']} for order {order_id}")

            return {
                'payment_id': str(payment.id),
                'razorpay_order_id': razorpay_order['id'],
                'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                'amount': order.total_amount,
                'currency': 'INR',
                'order_number': order.order_number,
                'description': f"Payment for order {order.order_number}"
            }

        except razorpay.errors.BadRequestError as e:
            logger.error(f"Razorpay order creation failed: {e}")
            raise BadRequestError(f"Payment gateway error: {str(e)}")

    async def verify_razorpay_payment(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str,
        user_id: UUID
    ) -> Payment:
        """
        Verify Razorpay payment signature and update payment status.

        Args:
            razorpay_order_id: Razorpay order ID
            razorpay_payment_id: Razorpay payment ID
            razorpay_signature: Payment signature
            user_id: User UUID

        Returns:
            Updated payment instance

        Raises:
            NotFoundError: If payment not found
            BadRequestError: If verification fails
        """
        # Get payment by Razorpay order ID
        payment = await self.payment_repository.get_by_order(
            UUID(razorpay_order_id)
        )
        if not payment and hasattr(payment, 'razorpay_order_id'):
            # Try to find by razorpay_order_id in metadata
            # This is a fallback - ideally we should have a proper column
            pass

        if not payment:
            raise NotFoundError("Payment not found")

        # Verify ownership
        if payment.user_id != user_id:
            raise BadRequestError("Unauthorized")

        # Verify signature
        if not self._verify_payment_signature(
            razorpay_order_id,
            razorpay_payment_id,
            razorpay_signature
        ):
            # Mark as failed
            await self.payment_repository.update_status(
                payment.id,
                PaymentStatus.FAILED,
                failure_reason="Signature verification failed"
            )
            raise BadRequestError("Payment verification failed")

        # Fetch payment details from Razorpay
        try:
            payment_details = self.razorpay_client.payment.fetch(razorpay_payment_id)

            # Update payment
            updated_payment = await self.payment_repository.update_status(
                payment.id,
                PaymentStatus.SUCCESS,
                razorpay_payment_id=razorpay_payment_id,
                razorpay_signature=razorpay_signature,
                transaction_id=razorpay_payment_id,
                paid_at=datetime.utcnow(),
                metadata={
                    **payment.metadata,
                    'payment_details': payment_details,
                    'verified_at': datetime.utcnow().isoformat()
                }
            )

            # Update order status
            order = await self.order_repository.get(payment.order_id)
            if order:
                await self.order_repository.update_status(
                    order.id,
                    OrderStatus.CONFIRMED
                )
                # Update payment fields on order
                order.payment_status = PaymentStatus.SUCCESS
                order.payment_id = razorpay_payment_id
                order.paid_at = datetime.utcnow()
                await self.order_repository.db.commit()

            logger.info(f"Payment verified: {razorpay_payment_id} for order {payment.order_id}")

            return updated_payment

        except Exception as e:
            logger.error(f"Payment verification error: {e}")
            await self.payment_repository.update_status(
                payment.id,
                PaymentStatus.FAILED,
                failure_reason=str(e)
            )
            raise BadRequestError(f"Payment verification failed: {str(e)}")

    async def process_cod_payment(
        self,
        order_id: UUID,
        user_id: UUID
    ) -> Payment:
        """
        Process Cash on Delivery payment.

        Args:
            order_id: Order UUID
            user_id: User UUID

        Returns:
            Created payment instance

        Raises:
            NotFoundError: If order not found
            BadRequestError: If validation fails
        """
        # Get order
        order = await self.order_repository.get(order_id)
        if not order:
            raise NotFoundError("Order not found")

        # Verify ownership
        if order.customer_id != user_id:
            raise BadRequestError("Unauthorized")

        # Check if payment already exists
        existing_payment = await self.payment_repository.get_by_order(order_id)
        if existing_payment:
            raise BadRequestError("Payment already exists for this order")

        # Create payment record
        payment_data = {
            'order_id': order_id,
            'user_id': user_id,
            'amount': order.total_amount,
            'currency': 'INR',
            'payment_method': PaymentMethod.COD,
            'status': PaymentStatus.PENDING,
            'metadata': {
                'note': 'Cash on Delivery - Payment collected at delivery',
                'created_at': datetime.utcnow().isoformat()
            }
        }

        payment = await self.payment_repository.create(payment_data)

        # Update order
        order.payment_status = PaymentStatus.PENDING
        order.payment_method = PaymentMethod.COD
        await self.order_repository.db.commit()

        logger.info(f"COD payment created for order {order_id}")

        return payment

    async def mark_cod_paid(
        self,
        payment_id: UUID,
        notes: Optional[str] = None
    ) -> Payment:
        """
        Mark COD payment as paid (called when delivery is completed).

        Args:
            payment_id: Payment UUID
            notes: Optional notes

        Returns:
            Updated payment

        Raises:
            NotFoundError: If payment not found
            BadRequestError: If not COD payment
        """
        payment = await self.payment_repository.get(payment_id)
        if not payment:
            raise NotFoundError("Payment not found")

        if payment.payment_method != PaymentMethod.COD:
            raise BadRequestError("Not a COD payment")

        # Update payment
        updated_payment = await self.payment_repository.update_status(
            payment_id,
            PaymentStatus.SUCCESS,
            paid_at=datetime.utcnow(),
            metadata={
                **payment.metadata,
                'collected_at': datetime.utcnow().isoformat(),
                'notes': notes
            }
        )

        # Update order
        order = await self.order_repository.get(payment.order_id)
        if order:
            order.payment_status = PaymentStatus.SUCCESS
            order.paid_at = datetime.utcnow()
            await self.order_repository.db.commit()

        logger.info(f"COD payment marked as paid: {payment_id}")

        return updated_payment

    async def refund_payment(
        self,
        payment_id: UUID,
        amount: Optional[float] = None,
        reason: Optional[str] = None
    ) -> Payment:
        """
        Initiate refund for a payment.

        Args:
            payment_id: Payment UUID
            amount: Refund amount (full refund if not specified)
            reason: Refund reason

        Returns:
            Updated payment

        Raises:
            NotFoundError: If payment not found
            BadRequestError: If refund not possible
        """
        payment = await self.payment_repository.get(payment_id)
        if not payment:
            raise NotFoundError("Payment not found")

        if payment.status != PaymentStatus.SUCCESS:
            raise BadRequestError("Cannot refund unsuccessful payment")

        refund_amount = amount or payment.amount

        if refund_amount > payment.amount:
            raise BadRequestError("Refund amount exceeds payment amount")

        # Process refund based on payment method
        if payment.payment_method == PaymentMethod.RAZORPAY:
            try:
                # Create refund in Razorpay
                refund = self.razorpay_client.payment.refund(
                    payment.razorpay_payment_id,
                    {
                        'amount': int(refund_amount * 100),  # Convert to paise
                        'notes': {'reason': reason or 'Customer refund request'}
                    }
                )

                # Update payment
                updated_payment = await self.payment_repository.update_status(
                    payment_id,
                    PaymentStatus.REFUNDED,
                    refund_amount=refund_amount,
                    refund_id=refund['id'],
                    refunded_at=datetime.utcnow(),
                    metadata={
                        **payment.metadata,
                        'refund': refund,
                        'refund_reason': reason
                    }
                )

                logger.info(f"Refund initiated: {refund['id']} for payment {payment_id}")

                return updated_payment

            except Exception as e:
                logger.error(f"Refund failed: {e}")
                raise BadRequestError(f"Refund failed: {str(e)}")

        elif payment.payment_method == PaymentMethod.COD:
            # Manual refund process for COD
            updated_payment = await self.payment_repository.update_status(
                payment_id,
                PaymentStatus.REFUNDED,
                refund_amount=refund_amount,
                refunded_at=datetime.utcnow(),
                metadata={
                    **payment.metadata,
                    'refund_reason': reason,
                    'refund_note': 'Manual refund for COD order'
                }
            )

            logger.info(f"COD refund marked: {payment_id}")

            return updated_payment

        else:
            raise BadRequestError(f"Refund not supported for {payment.payment_method.value}")

    def _verify_payment_signature(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str
    ) -> bool:
        """
        Verify Razorpay payment signature.

        Args:
            razorpay_order_id: Razorpay order ID
            razorpay_payment_id: Razorpay payment ID
            razorpay_signature: Signature to verify

        Returns:
            True if signature is valid
        """
        try:
            # Create signature
            message = f"{razorpay_order_id}|{razorpay_payment_id}"
            generated_signature = hmac.new(
                settings.RAZORPAY_KEY_SECRET.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(generated_signature, razorpay_signature)

        except Exception as e:
            logger.error(f"Signature verification error: {e}")
            return False
