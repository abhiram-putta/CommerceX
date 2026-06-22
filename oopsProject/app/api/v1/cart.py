"""
Cart management endpoints.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.config.database import get_db
from app.models.user import User
from app.repositories.cart_repository import CartRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.cart import (
    CartItemCreate,
    CartItemResponse,
    CartItemUpdate,
    CartResponse,
)
from app.schemas.common import MessageResponse
from app.services.cart_service import CartService

router = APIRouter()


def get_cart_service(db: AsyncSession = Depends(get_db)) -> CartService:
    """Get cart service dependency."""
    return CartService(
        CartRepository(db),
        ProductRepository(db),
        InventoryRepository(db)
    )


@router.get("", response_model=CartResponse)
async def get_cart(
    current_user: User = Depends(get_current_active_user),
    cart_service: CartService = Depends(get_cart_service),
) -> CartResponse:
    """
    Get current user's cart with all items and totals.
    """
    return await cart_service.get_user_cart(current_user.id)


@router.post("", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    item_data: CartItemCreate,
    current_user: User = Depends(get_current_active_user),
    cart_service: CartService = Depends(get_cart_service),
) -> CartItemResponse:
    """
    Add item to cart or update quantity if already exists.

    - **product_id**: Product UUID
    - **inventory_id**: Specific seller/inventory UUID
    - **quantity**: Quantity to add (1-100)
    """
    cart_item = await cart_service.add_to_cart(
        user_id=current_user.id,
        item_data=item_data
    )
    return CartItemResponse.model_validate(cart_item)


@router.put("/{cart_item_id}", response_model=CartItemResponse)
async def update_cart_item(
    cart_item_id: UUID,
    update_data: CartItemUpdate,
    current_user: User = Depends(get_current_active_user),
    cart_service: CartService = Depends(get_cart_service),
) -> CartItemResponse:
    """
    Update cart item quantity.

    - **cart_item_id**: Cart item UUID
    - **quantity**: New quantity (1-100)
    """
    cart_item = await cart_service.update_cart_item(
        user_id=current_user.id,
        cart_item_id=cart_item_id,
        quantity=update_data.quantity
    )
    return CartItemResponse.model_validate(cart_item)


@router.delete("/{cart_item_id}", response_model=MessageResponse)
async def remove_cart_item(
    cart_item_id: UUID,
    current_user: User = Depends(get_current_active_user),
    cart_service: CartService = Depends(get_cart_service),
) -> MessageResponse:
    """
    Remove item from cart.

    - **cart_item_id**: Cart item UUID to remove
    """
    success = await cart_service.remove_cart_item(
        user_id=current_user.id,
        cart_item_id=cart_item_id
    )

    if not success:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Cart item not found")

    return MessageResponse(message="Item removed from cart")


@router.delete("", response_model=MessageResponse)
async def clear_cart(
    current_user: User = Depends(get_current_active_user),
    cart_service: CartService = Depends(get_cart_service),
) -> MessageResponse:
    """
    Clear all items from cart.
    """
    await cart_service.clear_cart(current_user.id)
    return MessageResponse(message="Cart cleared successfully")


@router.get("/count", response_model=dict)
async def get_cart_count(
    current_user: User = Depends(get_current_active_user),
    cart_service: CartService = Depends(get_cart_service),
) -> dict:
    """
    Get count of items in cart (useful for cart badge).
    """
    count = await cart_service.get_cart_count(current_user.id)
    return {"count": count}
