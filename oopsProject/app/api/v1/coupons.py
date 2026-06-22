"""
Coupon API endpoints.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.dependencies import get_current_active_user, get_db
from app.models.user import User
from app.repositories.coupon_repository import CouponRepository, CouponUsageRepository
from app.repositories.order_repository import OrderRepository
from app.schemas.common import MessageResponse
from app.schemas.coupon import (
    CouponCreate,
    CouponResponse,
    CouponUpdate,
    CouponUsageResponse,
    CouponValidateRequest,
    CouponValidateResponse,
)
from app.services.coupon_service import CouponService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def get_coupon_service(db: AsyncSession = Depends(get_db)) -> CouponService:
    """Get coupon service instance."""
    return CouponService(
        coupon_repository=CouponRepository(db),
        usage_repository=CouponUsageRepository(db),
        order_repository=OrderRepository(db),
    )


@router.get("", response_model=List[CouponResponse])
async def get_available_coupons(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    coupon_service: CouponService = Depends(get_coupon_service),
):
    """
    Get available coupons for the current user.

    Returns list of coupons that user can use.
    """
    coupons = await coupon_service.get_available_coupons(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )
    return coupons


@router.post("/validate", response_model=CouponValidateResponse)
async def validate_coupon(
    request: CouponValidateRequest,
    current_user: User = Depends(get_current_active_user),
    coupon_service: CouponService = Depends(get_coupon_service),
):
    """
    Validate a coupon and calculate discount.

    - **code**: Coupon code to validate
    - **order_amount**: Order amount before discount
    - **product_ids**: List of product IDs in the order (optional)
    - **category_ids**: List of category IDs in the order (optional)

    Returns discount details if coupon is valid.
    """
    result = await coupon_service.validate_and_apply_coupon(
        code=request.code,
        user_id=current_user.id,
        order_amount=request.order_amount,
        product_ids=request.product_ids,
        category_ids=request.category_ids,
    )
    return result


@router.get("/history", response_model=List[CouponUsageResponse])
async def get_coupon_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    coupon_service: CouponService = Depends(get_coupon_service),
):
    """
    Get user's coupon usage history.

    Returns list of all coupons used by the user.
    """
    history = await coupon_service.get_user_coupon_history(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )
    return history


# Admin endpoints
@router.post("/admin", response_model=CouponResponse, status_code=status.HTTP_201_CREATED)
async def create_coupon(
    coupon_data: CouponCreate,
    current_user: User = Depends(get_current_active_user),
    coupon_service: CouponService = Depends(get_coupon_service),
):
    """
    Create a new coupon (Admin only).

    Creates a new discount coupon with specified parameters.
    """
    # TODO: Add admin role check
    # if current_user.role != UserRole.ADMIN:
    #     raise ForbiddenError("Admin access required")

    coupon = await coupon_service.create_coupon(coupon_data.model_dump())
    return coupon


@router.put("/admin/{coupon_id}", response_model=CouponResponse)
async def update_coupon(
    coupon_id: UUID,
    update_data: CouponUpdate,
    current_user: User = Depends(get_current_active_user),
    coupon_service: CouponService = Depends(get_coupon_service),
):
    """
    Update a coupon (Admin only).

    Updates coupon details.
    """
    # TODO: Add admin role check
    coupon = await coupon_service.update_coupon(
        coupon_id,
        update_data.model_dump(exclude_unset=True)
    )
    return coupon


@router.delete("/admin/{coupon_id}", response_model=MessageResponse)
async def deactivate_coupon(
    coupon_id: UUID,
    current_user: User = Depends(get_current_active_user),
    coupon_service: CouponService = Depends(get_coupon_service),
):
    """
    Deactivate a coupon (Admin only).

    Marks the coupon as inactive.
    """
    # TODO: Add admin role check
    await coupon_service.deactivate_coupon(coupon_id)
    return {"message": "Coupon deactivated successfully"}
