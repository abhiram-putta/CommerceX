"""
Full-text search API endpoints.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_db
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductListResponse
from app.services.search_service import SearchService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def get_search_service(db: AsyncSession = Depends(get_db)) -> SearchService:
    """Get search service instance."""
    return SearchService(product_repository=ProductRepository(db))


@router.get("", response_model=dict)
async def search_products(
    q: str = Query(..., min_length=1, description="Search query"),
    category_id: Optional[UUID] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    is_local: Optional[bool] = Query(None, description="Filter local products"),
    in_stock: bool = Query(True, description="Only show in-stock items"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search_service: SearchService = Depends(get_search_service),
):
    """
    Full-text search for products using PostgreSQL.

    **Search Features:**
    - Fast full-text search with ranking
    - Weighted search (name > description > brand)
    - Multiple word search (AND operation)
    - Quoted phrase search
    - Prefix matching (e.g., "lap" matches "laptop")

    **Filters:**
    - Category
    - Price range
    - Brand
    - Local products
    - Stock status

    **Returns:**
    - Paginated results with total count
    - Products ranked by relevance
    """
    skip = (page - 1) * page_size

    products, total = await search_service.search_products(
        query=q,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        brand=brand,
        is_local=is_local,
        in_stock=in_stock,
        skip=skip,
        limit=page_size,
    )

    # Calculate pagination metadata
    total_pages = (total + page_size - 1) // page_size

    return {
        "query": q,
        "results": [ProductListResponse.model_validate(p) for p in products],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
        "filters": {
            "category_id": str(category_id) if category_id else None,
            "min_price": min_price,
            "max_price": max_price,
            "brand": brand,
            "is_local": is_local,
            "in_stock": in_stock,
        }
    }


@router.get("/autocomplete", response_model=List[str])
async def autocomplete_search(
    q: str = Query(..., min_length=2, description="Search query (minimum 2 characters)"),
    limit: int = Query(10, ge=1, le=20, description="Maximum suggestions"),
    search_service: SearchService = Depends(get_search_service),
):
    """
    Get autocomplete suggestions for search query.

    **Usage:**
    - Type-ahead search suggestions
    - Minimum 2 characters required
    - Returns matching product names

    **Example:**
    - Query: "lap" → ["Laptop", "Laptop Bag", "Laptop Stand"]
    """
    suggestions = await search_service.autocomplete(q, limit)
    return suggestions


@router.get("/suggestions", response_model=dict)
async def search_suggestions(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(5, ge=1, le=10, description="Max suggestions per category"),
    search_service: SearchService = Depends(get_search_service),
):
    """
    Get categorized search suggestions.

    **Returns:**
    - Product name suggestions
    - Brand suggestions
    - Category suggestions

    **Usage:**
    - Rich search suggestions
    - Helps users refine search
    """
    suggestions = await search_service.search_suggest(q, limit)
    return suggestions


@router.get("/popular", response_model=List[str])
async def popular_searches(
    limit: int = Query(10, ge=1, le=20, description="Maximum results"),
    search_service: SearchService = Depends(get_search_service),
):
    """
    Get popular search terms.

    **Returns:**
    - Most searched terms
    - Trending products

    **Usage:**
    - Show popular searches to users
    - Search page suggestions
    - Homepage search hints
    """
    popular = await search_service.get_popular_searches(limit)
    return popular
