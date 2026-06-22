"""
Payment endpoints for payment processing.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.config.database import get_db
from app.models.user import User
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.schemas.common import MessageResponse
from app.schemas.payment import (
    PaymentInitiate,
    PaymentVerify,
    PaymentResponse,
    RefundRequest
)
from app.services.payment_service import PaymentService

router = APIRouter()


def get_payment_service(db: AsyncSession = Depends(get_db)) -> PaymentService:
    """Get payment service dependency."""
    return PaymentService(
        PaymentRepository(db),
        OrderRepository(db)
    )


@router.post("/initiate", response_model=dict, status_code=status.HTTP_201_CREATED)
async def initiate_payment(
    payment_data: PaymentInitiate,
    current_user: User = Depends(get_current_active_user),
    payment_service: PaymentService = Depends(get_payment_service),
) -> dict:
    """
    Initiate payment for an order.

    - **order_id**: Order UUID to pay for
    - **return_url**: Optional return URL after payment

    For Razorpay payments, this creates a Razorpay order and returns:
    - razorpay_order_id: Use this to open Razorpay checkout
    - razorpay_key_id: Your Razorpay public key
    - amount, currency, description: Order details

    For COD, this creates a pending payment record.
    """
    # Get the order to determine payment method
    order_repo = OrderRepository(payment_service.payment_repository.db)
    order = await order_repo.get(payment_data.order_id)

    if not order:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Order not found")

    # Check payment method
    if order.payment_method.value in ['RAZORPAY', 'UPI', 'CARD', 'NET_BANKING']:
        # Create Razorpay order
        result = await payment_service.create_razorpay_order(
            order_id=payment_data.order_id,
            user_id=current_user.id
        )
        return result
    elif order.payment_method.value == 'COD':
        # Create COD payment
        payment = await payment_service.process_cod_payment(
            order_id=payment_data.order_id,
            user_id=current_user.id
        )
        return {
            'payment_id': str(payment.id),
            'payment_method': 'COD',
            'status': 'PENDING',
            'message': 'Pay cash on delivery'
        }
    else:
        from app.core.exceptions import BadRequestError
        raise BadRequestError(f"Unsupported payment method: {order.payment_method.value}")


@router.post("/verify", response_model=PaymentResponse)
async def verify_payment(
    verification_data: PaymentVerify,
    current_user: User = Depends(get_current_active_user),
    payment_service: PaymentService = Depends(get_payment_service),
) -> PaymentResponse:
    """
    Verify Razorpay payment after checkout.

    - **payment_id**: Your internal payment ID
    - **payment_gateway_id**: Razorpay payment ID
    - **signature**: Razorpay signature for verification

    This endpoint:
    1. Verifies the payment signature
    2. Updates payment status to SUCCESS
    3. Updates order status to CONFIRMED
    4. Returns payment details

    Call this after user completes Razorpay checkout.
    """
    # Parse the razorpay data
    # payment_gateway_id should be in format "order_id" from Razorpay
    # We need to extract razorpay_order_id, razorpay_payment_id from the data

    # For simplicity, assuming payment_id is our internal payment UUID
    # and payment_gateway_id is razorpay_payment_id
    # signature is razorpay_signature

    # Get payment to find razorpay_order_id
    payment_repo = PaymentRepository(payment_service.payment_repository.db)
    payment = await payment_repo.get(UUID(verification_data.payment_id))

    if not payment:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Payment not found")

    razorpay_order_id = payment.razorpay_order_id

    # Verify payment
    verified_payment = await payment_service.verify_razorpay_payment(
        razorpay_order_id=razorpay_order_id,
        razorpay_payment_id=verification_data.payment_gateway_id,
        razorpay_signature=verification_data.signature,
        user_id=current_user.id
    )

    return PaymentResponse.model_validate(verified_payment)


@router.post("/{payment_id}/refund", response_model=PaymentResponse)
async def refund_payment(
    payment_id: UUID,
    refund_data: RefundRequest,
    current_user: User = Depends(get_current_active_user),
    payment_service: PaymentService = Depends(get_payment_service),
) -> PaymentResponse:
    """
    Initiate refund for a payment.

    - **payment_id**: Payment UUID
    - **amount**: Refund amount (optional, full refund if not specified)
    - **reason**: Refund reason (required)

    This endpoint:
    1. Validates payment exists and is successful
    2. Initiates refund with payment gateway (Razorpay)
    3. Updates payment status to REFUNDED
    4. Returns updated payment details

    For COD orders, this marks the refund as initiated for manual processing.
    """
    # Verify user owns this payment
    payment_repo = PaymentRepository(payment_service.payment_repository.db)
    payment = await payment_repo.get(payment_id)

    if not payment:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Payment not found")

    if payment.user_id != current_user.id:
        from app.core.exceptions import BadRequestError
        raise BadRequestError("Unauthorized to refund this payment")

    # Process refund
    refunded_payment = await payment_service.refund_payment(
        payment_id=payment_id,
        amount=refund_data.amount,
        reason=refund_data.reason
    )

    return PaymentResponse.model_validate(refunded_payment)


@router.get("/my-payments", response_model=List[PaymentResponse])
async def get_my_payments(
    current_user: User = Depends(get_current_active_user),
    payment_service: PaymentService = Depends(get_payment_service),
) -> List[PaymentResponse]:
    """
    Get all payments for the current user.

    Returns payment history in descending order (newest first).
    """
    payments = await payment_service.payment_repository.get_user_payments(
        user_id=current_user.id,
        skip=0,
        limit=100
    )
    return [PaymentResponse.model_validate(payment) for payment in payments]


@router.get("/order/{order_id}", response_model=PaymentResponse)
async def get_order_payment(
    order_id: UUID,
    current_user: User = Depends(get_current_active_user),
    payment_service: PaymentService = Depends(get_payment_service),
) -> PaymentResponse:
    """
    Get payment details for an order.

    - **order_id**: Order UUID

    Returns payment information for the specified order.
    """
    payment = await payment_service.payment_repository.get_by_order(order_id)

    if not payment:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Payment not found for this order")

    # Verify user owns the payment
    if payment.user_id != current_user.id:
        from app.core.exceptions import BadRequestError
        raise BadRequestError("Unauthorized to view this payment")

    return PaymentResponse.model_validate(payment)


@router.post("/{payment_id}/mark-cod-paid", response_model=PaymentResponse)
async def mark_cod_paid(
    payment_id: UUID,
    notes: str = None,
    current_user: User = Depends(get_current_active_user),
    payment_service: PaymentService = Depends(get_payment_service),
) -> PaymentResponse:
    """
    Mark COD payment as collected (for delivery personnel/admin).

    - **payment_id**: Payment UUID
    - **notes**: Optional delivery notes

    This should be called when cash is collected at delivery.
    Typically restricted to delivery personnel or admin role.
    """
    # TODO: Add role check for delivery personnel or admin
    payment = await payment_service.mark_cod_paid(
        payment_id=payment_id,
        notes=notes
    )

    return PaymentResponse.model_validate(payment)
