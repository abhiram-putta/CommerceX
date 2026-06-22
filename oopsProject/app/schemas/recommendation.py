"""
Recommendation schemas for API requests and responses.
"""
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.product import ProductListResponse


class RecommendationResponse(BaseModel):
    """Product recommendation with score."""
    product_id: UUID
    score: float = Field(..., ge=0.0, le=1.0)
    product: Optional[ProductListResponse] = None

    class Config:
        from_attributes = True


class PersonalizedRecommendationsResponse(BaseModel):
    """Response for personalized recommendations."""
    user_id: UUID
    recommendations: List[RecommendationResponse]
    total: int = Field(..., description="Total number of recommendations")
    algorithm: str = Field(..., description="Algorithm used for recommendations")

    class Config:
        from_attributes = True


class SimilarProductsResponse(BaseModel):
    """Response for similar product recommendations."""
    product_id: UUID
    similar_products: List[RecommendationResponse]
    total: int = Field(..., description="Total number of similar products")

    class Config:
        from_attributes = True
