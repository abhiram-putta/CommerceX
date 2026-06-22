"""
Order management endpoints.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.config.database import get_db
from app.models.user import User
from app.repositories.cart_repository import CartRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.order_repository import (
    OrderRepository,
    OrderItemRepository,
    OrderTrackingRepository
)
from app.repositories.product_repository import ProductRepository
from app.schemas.common import MessageResponse
from app.schemas.order import OrderCreate, OrderResponse, OrderTrackingResponse
from app.services.order_service import OrderService
from app.utils.enums import OrderStatus

router = APIRouter()


def get_order_service(db: AsyncSession = Depends(get_db)) -> OrderService:
    """Get order service dependency."""
    return OrderService(
        OrderRepository(db),
        OrderItemRepository(db),
        OrderTrackingRepository(db),
        ProductRepository(db),
        InventoryRepository(db),
        CartRepository(db)
    )


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    order_service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """
    Create a new order.

    - **items**: List of items to order (product_id, inventory_id, quantity)
    - **order_type**: ONLINE, IN_STORE, etc.
    - **payment_method**: Payment method
    - **delivery_address**: Delivery address details
    - **delivery_notes**: Optional delivery notes
    - **scheduled_delivery_date**: Optional scheduled delivery date

    This will:
    1. Validate all items and check stock
    2. Calculate totals (subtotal, tax, delivery charge)
    3. Create order and order items
    4. Reduce inventory stock
    5. Clear cart (for online orders)
    6. Initialize order tracking
    """
    order = await order_service.create_order(
        user_id=current_user.id,
        order_data=order_data
    )
    return OrderResponse.model_validate(order)


@router.get("", response_model=List[OrderResponse])
async def get_user_orders(
    status: Optional[OrderStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    order_service: OrderService = Depends(get_order_service),
) -> List[OrderResponse]:
    """
    Get all orders for the current user.

    - **status**: Optional filter by order status
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)

    Returns user's order history in descending order (newest first).
    """
    skip = (page - 1) * page_size
    orders = await order_service.get_user_orders(
        user_id=current_user.id,
        status=status,
        skip=skip,
        limit=page_size
    )
    return [OrderResponse.model_validate(order) for order in orders]


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    current_user: User = Depends(get_current_active_user),
    order_service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """
    Get order details by ID.

    - **order_id**: Order UUID

    Returns complete order details including items and tracking history.
    """
    order = await order_service.get_order(
        order_id=order_id,
        user_id=current_user.id
    )
    return OrderResponse.model_validate(order)


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: UUID,
    reason: str = Query(..., min_length=5, max_length=500),
    current_user: User = Depends(get_current_active_user),
    order_service: OrderService = Depends(get_order_service),
) -> OrderResponse:
    """
    Cancel an order.

    - **order_id**: Order UUID
    - **reason**: Cancellation reason (5-500 characters)

    Can only cancel orders with status PENDING or CONFIRMED.
    This will:
    1. Update order status to CANCELLED
    2. Restore inventory stock
    3. Add tracking entry
    """
    order = await order_service.cancel_order(
        order_id=order_id,
        user_id=current_user.id,
        reason=reason
    )
    return OrderResponse.model_validate(order)


@router.get("/{order_id}/tracking", response_model=List[OrderTrackingResponse])
async def get_order_tracking(
    order_id: UUID,
    current_user: User = Depends(get_current_active_user),
    order_service: OrderService = Depends(get_order_service),
) -> List[OrderTrackingResponse]:
    """
    Get order tracking history.

    - **order_id**: Order UUID

    Returns all tracking updates for the order in descending order (newest first).
    """
    tracking = await order_service.get_order_tracking(
        order_id=order_id,
        user_id=current_user.id
    )
    return [OrderTrackingResponse.model_validate(t) for t in tracking]
