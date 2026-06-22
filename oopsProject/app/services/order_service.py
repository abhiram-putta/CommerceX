"""
Order service for order management business logic.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.order import Order, OrderItem
from app.repositories.cart_repository import CartRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.order_repository import (
    OrderRepository,
    OrderItemRepository,
    OrderTrackingRepository
)
from app.repositories.product_repository import ProductRepository
from app.schemas.order import OrderCreate, OrderResponse
from app.services.email_service import email_service
from app.utils.enums import OrderStatus, OrderType, PaymentStatus
from app.utils.helpers import generate_order_number
from app.utils.logger import get_logger

logger = get_logger(__name__)


class OrderService:
    """Order service with business logic."""

    def __init__(
        self,
        order_repository: OrderRepository,
        order_item_repository: OrderItemRepository,
        tracking_repository: OrderTrackingRepository,
        product_repository: ProductRepository,
        inventory_repository: InventoryRepository,
        cart_repository: CartRepository
    ):
        """Initialize order service."""
        self.order_repository = order_repository
        self.order_item_repository = order_item_repository
        self.tracking_repository = tracking_repository
        self.product_repository = product_repository
        self.inventory_repository = inventory_repository
        self.cart_repository = cart_repository

    async def create_order(
        self,
        user_id: UUID,
        order_data: OrderCreate
    ) -> Order:
        """
        Create new order from cart or direct items.

        Args:
            user_id: Customer UUID
            order_data: Order creation data

        Returns:
            Created order

        Raises:
            BadRequestError: If validation fails
            NotFoundError: If product/inventory not found
        """
        # Validate and calculate order totals
        subtotal = 0.0
        order_items_data = []

        for item in order_data.items:
            # Verify product
            product = await self.product_repository.get(item.product_id)
            if not product:
                raise NotFoundError(f"Product {item.product_id} not found")

            # Verify inventory
            inventory = await self.inventory_repository.get(item.inventory_id)
            if not inventory:
                raise NotFoundError(f"Inventory {item.inventory_id} not found")

            # Check stock
            if not await self.inventory_repository.check_availability(
                item.inventory_id,
                item.quantity
            ):
                raise BadRequestError(
                    f"Insufficient stock for {product.name}. "
                    f"Available: {inventory.stock_quantity}"
                )

            # Calculate item total
            unit_price = inventory.price
            item_total = unit_price * item.quantity
            subtotal += item_total

            order_items_data.append({
                'product_id': item.product_id,
                'product_name': product.name,
                'quantity': item.quantity,
                'unit_price': unit_price,
                'discount_percentage': 0.0,
                'total_price': item_total,
                'inventory_id': item.inventory_id
            })

        # Calculate totals
        tax_rate = 0.18  # 18% GST
        tax_amount = subtotal * tax_rate
        delivery_charge = 50.0 if subtotal < 500 else 0.0  # Free delivery over ₹500
        total_amount = subtotal + tax_amount + delivery_charge

        # Create order
        order_number = generate_order_number()
        order_dict = {
            'order_number': order_number,
            'customer_id': user_id,
            'order_type': order_data.order_type,
            'subtotal_amount': subtotal,
            'discount_amount': 0.0,
            'tax_amount': tax_amount,
            'delivery_charge': delivery_charge,
            'total_amount': total_amount,
            'payment_status': PaymentStatus.PENDING,
            'payment_method': order_data.payment_method,
            'delivery_address': order_data.delivery_address,
            'scheduled_delivery_date': order_data.scheduled_delivery_date,
            'status': OrderStatus.PENDING,
            'delivery_notes': order_data.delivery_notes
        }

        order = await self.order_repository.create(order_dict)

        # Create order items
        for item_data in order_items_data:
            item_data['order_id'] = order.id
            await self.order_item_repository.create(item_data)

        # Add initial tracking
        await self.tracking_repository.add_tracking_update(
            order_id=order.id,
            status=OrderStatus.PENDING,
            notes="Order placed successfully"
        )

        # Clear cart if order type is online
        if order_data.order_type == OrderType.ONLINE:
            await self.cart_repository.clear_user_cart(user_id)

        # Reduce inventory stock
        for item in order_data.items:
            await self.inventory_repository.update_stock(
                item.inventory_id,
                -item.quantity
            )

        logger.info(f"Order created: {order_number} for user {user_id}")

        # Send order confirmation email
        try:
            # Get user details for email
            from app.repositories.user_repository import UserRepository
            user_repo = UserRepository(self.order_repository.db)
            user = await user_repo.get(user_id)

            if user and user.email:
                # Prepare order items for email
                email_items = []
                for item_data in order_items_data:
                    email_items.append({
                        'product_name': item_data['product_name'],
                        'quantity': item_data['quantity'],
                        'unit_price': item_data['unit_price'],
                        'total_price': item_data['total_price'],
                    })

                # Send confirmation email
                await email_service.send_order_confirmation(
                    to_email=user.email,
                    customer_name=user.profile.full_name if user.profile else user.email,
                    order_id=order.id,
                    order_number=order_number,
                    order_date=order.created_at,
                    items=email_items,
                    subtotal=subtotal,
                    tax=tax_amount,
                    shipping=delivery_charge,
                    total=total_amount,
                    shipping_address=order_data.delivery_address
                )
                logger.info(f"Order confirmation email sent to {user.email}")
        except Exception as e:
            # Don't fail order creation if email fails
            logger.error(f"Failed to send order confirmation email: {e}")

        # Return with loaded relationships
        return await self.order_repository.get_with_items(order.id)

    async def get_order(self, order_id: UUID, user_id: UUID) -> Order:
        """
        Get order details.

        Args:
            order_id: Order UUID
            user_id: User UUID (for verification)

        Returns:
            Order instance

        Raises:
            NotFoundError: If order not found
            BadRequestError: If unauthorized
        """
        order = await self.order_repository.get_with_items(order_id)

        if not order:
            raise NotFoundError("Order not found")

        if order.customer_id != user_id:
            raise BadRequestError("Unauthorized to view this order")

        return order

    async def get_user_orders(
        self,
        user_id: UUID,
        status: Optional[OrderStatus] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """
        Get all orders for a user.

        Args:
            user_id: User UUID
            status: Optional status filter
            skip: Skip N records
            limit: Limit results

        Returns:
            List of orders
        """
        return await self.order_repository.get_user_orders(
            user_id,
            status,
            skip,
            limit
        )

    async def cancel_order(
        self,
        order_id: UUID,
        user_id: UUID,
        reason: str
    ) -> Order:
        """
        Cancel an order.

        Args:
            order_id: Order UUID
            user_id: User UUID
            reason: Cancellation reason

        Returns:
            Updated order

        Raises:
            NotFoundError: If order not found
            BadRequestError: If cannot cancel
        """
        order = await self.order_repository.get_with_items(order_id)

        if not order:
            raise NotFoundError("Order not found")

        if order.customer_id != user_id:
            raise BadRequestError("Unauthorized to cancel this order")

        # Can only cancel pending or confirmed orders
        if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
            raise BadRequestError(
                f"Cannot cancel order with status: {order.status.value}"
            )

        # Update order status
        order.status = OrderStatus.CANCELLED
        order.cancellation_reason = reason
        await self.order_repository.db.commit()

        # Add tracking
        await self.tracking_repository.add_tracking_update(
            order_id=order.id,
            status=OrderStatus.CANCELLED,
            notes=f"Order cancelled: {reason}"
        )

        # Restore inventory
        for item in order.items:
            if hasattr(item, 'inventory_id'):
                await self.inventory_repository.update_stock(
                    item.inventory_id,
                    item.quantity  # Add back to stock
                )

        logger.info(f"Order cancelled: {order.order_number}")

        return await self.order_repository.get_with_items(order_id)

    async def get_order_tracking(self, order_id: UUID, user_id: UUID) -> List:
        """
        Get order tracking history.

        Args:
            order_id: Order UUID
            user_id: User UUID (for verification)

        Returns:
            List of tracking entries

        Raises:
            NotFoundError: If order not found
            BadRequestError: If unauthorized
        """
        order = await self.order_repository.get(order_id)

        if not order:
            raise NotFoundError("Order not found")

        if order.customer_id != user_id:
            raise BadRequestError("Unauthorized to view this order")

        return await self.tracking_repository.get_by_order(order_id)
