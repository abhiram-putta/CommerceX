"""
Review service for review management business logic.
"""
from typing import List, Optional
from uuid import UUID

from app.core.exceptions import BadRequestError, NotFoundError
from app.models.review import Review
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.review_repository import ReviewRepository
from app.schemas.review import ReviewCreate, ReviewUpdate
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ReviewService:
    """Review service with business logic."""

    def __init__(
        self,
        review_repository: ReviewRepository,
        product_repository: ProductRepository,
        order_repository: OrderRepository
    ):
        """Initialize review service."""
        self.review_repository = review_repository
        self.product_repository = product_repository
        self.order_repository = order_repository

    async def create_review(
        self,
        user_id: UUID,
        review_data: ReviewCreate
    ) -> Review:
        """
        Create a new review.

        Args:
            user_id: User UUID
            review_data: Review creation data

        Returns:
            Created review

        Raises:
            NotFoundError: If product not found
            BadRequestError: If user already reviewed
        """
        # Verify product exists
        product = await self.product_repository.get(review_data.product_id)
        if not product:
            raise NotFoundError("Product not found")

        # Check if user already reviewed this product
        existing_review = await self.review_repository.get_user_product_review(
            user_id,
            review_data.product_id
        )
        if existing_review:
            raise BadRequestError("You have already reviewed this product")

        # Check if verified purchase
        is_verified = False
        if review_data.order_id:
            order = await self.order_repository.get(review_data.order_id)
            if order and order.customer_id == user_id:
                # Verify order contains this product
                for item in order.items:
                    if item.product_id == review_data.product_id:
                        is_verified = True
                        break

        # Create review
        review_dict = {
            'user_id': user_id,
            'product_id': review_data.product_id,
            'order_id': review_data.order_id,
            'rating': review_data.rating,
            'title': review_data.title,
            'comment': review_data.comment,
            'images': review_data.images,
            'is_verified_purchase': is_verified,
            'is_approved': True,  # Auto-approve for now
            'helpful_count': 0
        }

        review = await self.review_repository.create(review_dict)
        logger.info(f"Review created: {review.id} for product {review_data.product_id}")

        return review

    async def update_review(
        self,
        review_id: UUID,
        user_id: UUID,
        review_data: ReviewUpdate
    ) -> Review:
        """
        Update a review.

        Args:
            review_id: Review UUID
            user_id: User UUID
            review_data: Review update data

        Returns:
            Updated review

        Raises:
            NotFoundError: If review not found
            BadRequestError: If unauthorized
        """
        review = await self.review_repository.get(review_id)
        if not review:
            raise NotFoundError("Review not found")

        if review.user_id != user_id:
            raise BadRequestError("Unauthorized to update this review")

        # Update review
        update_dict = review_data.model_dump(exclude_unset=True)
        updated_review = await self.review_repository.update(review_id, update_dict)

        logger.info(f"Review updated: {review_id}")
        return updated_review

    async def delete_review(
        self,
        review_id: UUID,
        user_id: UUID
    ) -> bool:
        """
        Delete a review.

        Args:
            review_id: Review UUID
            user_id: User UUID

        Returns:
            True if successful

        Raises:
            NotFoundError: If review not found
            BadRequestError: If unauthorized
        """
        review = await self.review_repository.get(review_id)
        if not review:
            raise NotFoundError("Review not found")

        if review.user_id != user_id:
            raise BadRequestError("Unauthorized to delete this review")

        success = await self.review_repository.delete(review_id)
        logger.info(f"Review deleted: {review_id}")

        return success

    async def get_product_reviews(
        self,
        product_id: UUID,
        verified_only: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[Review]:
        """
        Get reviews for a product.

        Args:
            product_id: Product UUID
            verified_only: Only return verified purchase reviews
            skip: Skip N records
            limit: Limit results

        Returns:
            List of reviews
        """
        return await self.review_repository.get_product_reviews(
            product_id,
            verified_only,
            skip,
            limit
        )

    async def get_user_reviews(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Review]:
        """
        Get reviews by a user.

        Args:
            user_id: User UUID
            skip: Skip N records
            limit: Limit results

        Returns:
            List of reviews
        """
        return await self.review_repository.get_user_reviews(
            user_id,
            skip,
            limit
        )

    async def get_product_rating_summary(self, product_id: UUID) -> dict:
        """
        Get rating summary for a product.

        Args:
            product_id: Product UUID

        Returns:
            Dict with average rating, total reviews, and rating distribution
        """
        avg_rating = await self.review_repository.get_average_rating(product_id)
        rating_counts = await self.review_repository.get_rating_counts(product_id)
        total_reviews = await self.review_repository.count_product_reviews(product_id)

        return {
            'product_id': str(product_id),
            'average_rating': round(avg_rating, 2) if avg_rating else 0.0,
            'total_reviews': total_reviews,
            'rating_distribution': rating_counts,
            'verified_percentage': 0  # TODO: Calculate verified percentage
        }
