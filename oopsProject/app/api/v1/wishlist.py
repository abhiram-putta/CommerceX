"""
Wishlist management endpoints.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.config.database import get_db
from app.models.user import User
from app.repositories.product_repository import ProductRepository
from app.repositories.wishlist_repository import WishlistRepository
from app.schemas.common import MessageResponse
from app.schemas.wishlist import (
    WishlistCheckResponse,
    WishlistCountResponse,
    WishlistItemCreate,
    WishlistItemResponse,
)
from app.services.wishlist_service import WishlistService

router = APIRouter()


def get_wishlist_service(db: AsyncSession = Depends(get_db)) -> WishlistService:
    """Get wishlist service dependency."""
    return WishlistService(
        WishlistRepository(db),
        ProductRepository(db)
    )


@router.get("", response_model=List[WishlistItemResponse])
async def get_wishlist(
    current_user: User = Depends(get_current_active_user),
    wishlist_service: WishlistService = Depends(get_wishlist_service),
) -> List[WishlistItemResponse]:
    """
    Get user's wishlist.

    Returns list of wishlist items with product details.
    """
    items = await wishlist_service.get_user_wishlist(current_user.id)
    return items


@router.post("", response_model=WishlistItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(
    item: WishlistItemCreate,
    current_user: User = Depends(get_current_active_user),
    wishlist_service: WishlistService = Depends(get_wishlist_service),
) -> WishlistItemResponse:
    """
    Add product to wishlist.

    - Validates product exists
    - Checks if already in wishlist
    - Creates wishlist item
    """
    wishlist_item = await wishlist_service.add_to_wishlist(
        current_user.id,
        item.product_id
    )
    return wishlist_item


@router.delete("/{product_id}", response_model=MessageResponse)
async def remove_from_wishlist(
    product_id: UUID,
    current_user: User = Depends(get_current_active_user),
    wishlist_service: WishlistService = Depends(get_wishlist_service),
) -> MessageResponse:
    """
    Remove product from wishlist.

    Returns success message if removed.
    """
    await wishlist_service.remove_from_wishlist(current_user.id, product_id)
    return MessageResponse(message="Product removed from wishlist")


@router.delete("", response_model=MessageResponse)
async def clear_wishlist(
    current_user: User = Depends(get_current_active_user),
    wishlist_service: WishlistService = Depends(get_wishlist_service),
) -> MessageResponse:
    """
    Clear all items from wishlist.

    Returns number of items removed.
    """
    count = await wishlist_service.clear_wishlist(current_user.id)
    return MessageResponse(message=f"Cleared {count} items from wishlist")


@router.get("/count", response_model=WishlistCountResponse)
async def get_wishlist_count(
    current_user: User = Depends(get_current_active_user),
    wishlist_service: WishlistService = Depends(get_wishlist_service),
) -> WishlistCountResponse:
    """
    Get count of items in wishlist.

    Useful for wishlist badge display.
    """
    count = await wishlist_service.get_wishlist_count(current_user.id)
    return WishlistCountResponse(count=count)


@router.get("/check/{product_id}", response_model=WishlistCheckResponse)
async def check_in_wishlist(
    product_id: UUID,
    current_user: User = Depends(get_current_active_user),
    wishlist_service: WishlistService = Depends(get_wishlist_service),
) -> WishlistCheckResponse:
    """
    Check if product is in wishlist.

    Returns boolean indicating if product is wishlisted.
    """
    in_wishlist = await wishlist_service.is_in_wishlist(
        current_user.id,
        product_id
    )
    return WishlistCheckResponse(
        in_wishlist=in_wishlist,
        product_id=product_id
    )
