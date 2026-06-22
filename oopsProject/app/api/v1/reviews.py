"""
Review management endpoints.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.config.database import get_db
from app.models.user import User
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.review_repository import ReviewRepository
from app.schemas.common import MessageResponse
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewUpdate
from app.services.review_service import ReviewService

router = APIRouter()


def get_review_service(db: AsyncSession = Depends(get_db)) -> ReviewService:
    """Get review service dependency."""
    return ReviewService(
        ReviewRepository(db),
        ProductRepository(db),
        OrderRepository(db)
    )


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_active_user),
    review_service: ReviewService = Depends(get_review_service),
) -> ReviewResponse:
    """
    Create a new product review.

    - **product_id**: Product to review
    - **order_id**: Optional order ID (for verified purchase)
    - **rating**: Rating from 1-5 stars
    - **title**: Optional review title
    - **comment**: Optional review text
    - **images**: Optional list of image URLs

    Users can only review each product once.
    """
    review = await review_service.create_review(
        user_id=current_user.id,
        review_data=review_data
    )
    return ReviewResponse.model_validate(review)


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: UUID,
    review_data: ReviewUpdate,
    current_user: User = Depends(get_current_active_user),
    review_service: ReviewService = Depends(get_review_service),
) -> ReviewResponse:
    """
    Update your review.

    - **review_id**: Review UUID
    - **rating**: Optional new rating
    - **title**: Optional new title
    - **comment**: Optional new comment
    - **images**: Optional new images

    Only the review author can update their review.
    """
    review = await review_service.update_review(
        review_id=review_id,
        user_id=current_user.id,
        review_data=review_data
    )
    return ReviewResponse.model_validate(review)


@router.delete("/{review_id}", response_model=MessageResponse)
async def delete_review(
    review_id: UUID,
    current_user: User = Depends(get_current_active_user),
    review_service: ReviewService = Depends(get_review_service),
) -> MessageResponse:
    """
    Delete your review.

    - **review_id**: Review UUID

    Only the review author can delete their review.
    """
    success = await review_service.delete_review(
        review_id=review_id,
        user_id=current_user.id
    )

    if not success:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Review not found")

    return MessageResponse(message="Review deleted successfully")


@router.get("/product/{product_id}", response_model=List[ReviewResponse])
async def get_product_reviews(
    product_id: UUID,
    verified_only: bool = Query(False, description="Only verified purchases"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    review_service: ReviewService = Depends(get_review_service),
) -> List[ReviewResponse]:
    """
    Get reviews for a product.

    - **product_id**: Product UUID
    - **verified_only**: Filter for verified purchase reviews only
    - **page**: Page number
    - **page_size**: Items per page

    Returns reviews in descending order (newest first).
    """
    skip = (page - 1) * page_size
    reviews = await review_service.get_product_reviews(
        product_id=product_id,
        verified_only=verified_only,
        skip=skip,
        limit=page_size
    )
    return [ReviewResponse.model_validate(review) for review in reviews]


@router.get("/user/{user_id}", response_model=List[ReviewResponse])
async def get_user_reviews(
    user_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    review_service: ReviewService = Depends(get_review_service),
) -> List[ReviewResponse]:
    """
    Get reviews by a specific user.

    - **user_id**: User UUID
    - **page**: Page number
    - **page_size**: Items per page

    Returns user's reviews in descending order (newest first).
    """
    skip = (page - 1) * page_size
    reviews = await review_service.get_user_reviews(
        user_id=user_id,
        skip=skip,
        limit=page_size
    )
    return [ReviewResponse.model_validate(review) for review in reviews]


@router.get("/my-reviews", response_model=List[ReviewResponse])
async def get_my_reviews(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    review_service: ReviewService = Depends(get_review_service),
) -> List[ReviewResponse]:
    """
    Get your own reviews.

    - **page**: Page number
    - **page_size**: Items per page

    Returns your reviews in descending order (newest first).
    """
    skip = (page - 1) * page_size
    reviews = await review_service.get_user_reviews(
        user_id=current_user.id,
        skip=skip,
        limit=page_size
    )
    return [ReviewResponse.model_validate(review) for review in reviews]


@router.get("/product/{product_id}/summary", response_model=dict)
async def get_product_rating_summary(
    product_id: UUID,
    review_service: ReviewService = Depends(get_review_service),
) -> dict:
    """
    Get rating summary for a product.

    - **product_id**: Product UUID

    Returns:
    - Average rating
    - Total review count
    - Rating distribution (1-5 stars)
    - Verified purchase percentage
    """
    return await review_service.get_product_rating_summary(product_id)
