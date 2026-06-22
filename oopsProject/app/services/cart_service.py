"""
Cart service for cart management business logic.
"""
from typing import List, Optional
from uuid import UUID

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.cart import Cart
from app.repositories.cart_repository import CartRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.cart import CartItemCreate, CartResponse, CartItemResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CartService:
    """Cart service with business logic."""

    def __init__(
        self,
        cart_repository: CartRepository,
        product_repository: ProductRepository,
        inventory_repository: InventoryRepository
    ):
        """
        Initialize cart service.

        Args:
            cart_repository: Cart repository instance
            product_repository: Product repository instance
            inventory_repository: Inventory repository instance
        """
        self.cart_repository = cart_repository
        self.product_repository = product_repository
        self.inventory_repository = inventory_repository

    async def get_user_cart(self, user_id: UUID) -> CartResponse:
        """
        Get user's cart with all items.

        Args:
            user_id: User UUID

        Returns:
            CartResponse with all items and totals
        """
        cart_items = await self.cart_repository.get_user_cart_items(
            user_id,
            include_product=True
        )

        # Convert to response schema
        items_response = [
            CartItemResponse.model_validate(item) for item in cart_items
        ]

        # Calculate totals
        subtotal = sum(item.subtotal for item in cart_items)
        tax_rate = 0.18  # 18% GST
        estimated_tax = subtotal * tax_rate
        estimated_total = subtotal + estimated_tax

        return CartResponse(
            items=items_response,
            total_items=len(cart_items),
            subtotal=subtotal,
            estimated_tax=estimated_tax,
            estimated_total=estimated_total
        )

    async def add_to_cart(
        self,
        user_id: UUID,
        item_data: CartItemCreate
    ) -> Cart:
        """
        Add item to cart or update quantity if already exists.

        Args:
            user_id: User UUID
            item_data: Cart item data

        Returns:
            Cart item instance

        Raises:
            NotFoundError: If product or inventory not found
            BadRequestError: If insufficient stock
        """
        # Verify product exists
        product = await self.product_repository.get(item_data.product_id)
        if not product:
            raise NotFoundError("Product not found")

        # Verify inventory exists
        inventory = await self.inventory_repository.get(item_data.inventory_id)
        if not inventory:
            raise NotFoundError("Inventory not found")

        # Check if product matches inventory
        if inventory.product_id != item_data.product_id:
            raise BadRequestError("Inventory does not match product")

        # Check stock availability
        if inventory.stock_quantity < item_data.quantity:
            raise BadRequestError(
                f"Insufficient stock. Available: {inventory.stock_quantity}"
            )

        # Check if item already in cart
        existing_item = await self.cart_repository.get_cart_item(
            user_id=user_id,
            product_id=item_data.product_id,
            inventory_id=item_data.inventory_id
        )

        if existing_item:
            # Update quantity
            new_quantity = existing_item.quantity + item_data.quantity

            # Verify stock for new quantity
            if inventory.stock_quantity < new_quantity:
                raise BadRequestError(
                    f"Insufficient stock. Available: {inventory.stock_quantity}, "
                    f"In cart: {existing_item.quantity}"
                )

            updated_item = await self.cart_repository.update_quantity(
                existing_item.id,
                new_quantity
            )
            logger.info(f"Updated cart item quantity: {updated_item.id}")
            return updated_item

        # Create new cart item
        cart_item_data = {
            'user_id': user_id,
            'product_id': item_data.product_id,
            'inventory_id': item_data.inventory_id,
            'quantity': item_data.quantity,
            'price_at_addition': inventory.price,  # Snapshot price
            'is_active': True
        }

        cart_item = await self.cart_repository.create(cart_item_data)
        logger.info(f"Added item to cart: {cart_item.id}")

        return cart_item

    async def update_cart_item(
        self,
        user_id: UUID,
        cart_item_id: UUID,
        quantity: int
    ) -> Cart:
        """
        Update cart item quantity.

        Args:
            user_id: User UUID
            cart_item_id: Cart item UUID
            quantity: New quantity

        Returns:
            Updated cart item

        Raises:
            NotFoundError: If cart item not found
            BadRequestError: If insufficient stock or unauthorized
        """
        # Get cart item
        cart_item = await self.cart_repository.get(cart_item_id)
        if not cart_item:
            raise NotFoundError("Cart item not found")

        # Verify ownership
        if cart_item.user_id != user_id:
            raise BadRequestError("Unauthorized to modify this cart item")

        # Check stock availability
        inventory = await self.inventory_repository.get(cart_item.inventory_id)
        if inventory.stock_quantity < quantity:
            raise BadRequestError(
                f"Insufficient stock. Available: {inventory.stock_quantity}"
            )

        # Update quantity
        updated_item = await self.cart_repository.update_quantity(
            cart_item_id,
            quantity
        )

        logger.info(f"Updated cart item: {cart_item_id} to quantity: {quantity}")
        return updated_item

    async def remove_cart_item(
        self,
        user_id: UUID,
        cart_item_id: UUID
    ) -> bool:
        """
        Remove item from cart.

        Args:
            user_id: User UUID
            cart_item_id: Cart item UUID

        Returns:
            True if successful

        Raises:
            NotFoundError: If cart item not found
            BadRequestError: If unauthorized
        """
        # Get cart item
        cart_item = await self.cart_repository.get(cart_item_id)
        if not cart_item:
            raise NotFoundError("Cart item not found")

        # Verify ownership
        if cart_item.user_id != user_id:
            raise BadRequestError("Unauthorized to remove this cart item")

        # Remove item
        success = await self.cart_repository.remove_item(cart_item_id)

        if success:
            logger.info(f"Removed cart item: {cart_item_id}")

        return success

    async def clear_cart(self, user_id: UUID) -> bool:
        """
        Clear all items from user's cart.

        Args:
            user_id: User UUID

        Returns:
            True if successful
        """
        success = await self.cart_repository.clear_user_cart(user_id)

        if success:
            logger.info(f"Cleared cart for user: {user_id}")

        return success

    async def get_cart_count(self, user_id: UUID) -> int:
        """
        Get count of items in user's cart.

        Args:
            user_id: User UUID

        Returns:
            Number of items in cart
        """
        cart_items = await self.cart_repository.get_user_cart_items(
            user_id,
            include_product=False
        )
        return len(cart_items)
