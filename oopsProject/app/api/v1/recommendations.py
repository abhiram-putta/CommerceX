"""
Recommendation endpoints for ML-based product recommendations.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.config.database import get_db
from app.models.user import User
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductListResponse
from app.schemas.recommendation import (
    PersonalizedRecommendationsResponse,
    RecommendationResponse,
    SimilarProductsResponse,
)
from app.services.recommendation_service import RecommendationService

router = APIRouter()


def get_recommendation_service(db: AsyncSession = Depends(get_db)) -> RecommendationService:
    """Get recommendation service dependency."""
    return RecommendationService(ProductRepository(db))


@router.get("/for-you", response_model=PersonalizedRecommendationsResponse)
async def get_personalized_recommendations(
    top_n: int = Query(10, ge=1, le=50, description="Number of recommendations"),
    current_user: User = Depends(get_current_active_user),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
) -> PersonalizedRecommendationsResponse:
    """
    Get personalized product recommendations for the current user.
    Uses collaborative filtering to recommend products based on user behavior.
    """
    # Get recommendations
    recommendations_raw = await recommendation_service.get_personalized_recommendations(
        user_id=current_user.id,
        top_n=top_n
    )

    # Fetch product details
    recommendations = []
    for product_id, score in recommendations_raw:
        product = await recommendation_service.product_repository.get(product_id)
        if product:
            rec = RecommendationResponse(
                product_id=product_id,
                score=score,
                product=ProductListResponse.model_validate(product)
            )
            recommendations.append(rec)

    return PersonalizedRecommendationsResponse(
        user_id=current_user.id,
        recommendations=recommendations,
        total=len(recommendations),
        algorithm="collaborative_filtering"
    )


@router.get("/similar/{product_id}", response_model=SimilarProductsResponse)
async def get_similar_products(
    product_id: UUID,
    top_n: int = Query(10, ge=1, le=50, description="Number of similar products"),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
) -> SimilarProductsResponse:
    """
    Get products similar to a given product.
    Uses semantic search to find products with similar descriptions and features.
    """
    # Check if product exists
    product = await recommendation_service.product_repository.get(product_id)
    if not product:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Product not found")

    # Get similar products
    similar_raw = await recommendation_service.get_similar_products(
        product_id=product_id,
        top_n=top_n
    )

    # Fetch product details
    similar_products = []
    for similar_id, score in similar_raw:
        similar_product = await recommendation_service.product_repository.get(similar_id)
        if similar_product:
            rec = RecommendationResponse(
                product_id=similar_id,
                score=score,
                product=ProductListResponse.model_validate(similar_product)
            )
            similar_products.append(rec)

    return SimilarProductsResponse(
        product_id=product_id,
        similar_products=similar_products,
        total=len(similar_products)
    )


@router.get("/trending", response_model=List[ProductListResponse])
async def get_trending_products(
    top_n: int = Query(10, ge=1, le=50, description="Number of trending products"),
    category_id: UUID = Query(None, description="Filter by category"),
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
) -> List[ProductListResponse]:
    """
    Get trending products.
    Returns popular products based on recent user interactions.
    """
    products = await recommendation_service.get_trending_products(
        top_n=top_n,
        category_id=category_id
    )
    return [ProductListResponse.model_validate(p) for p in products]
