"""
Product management endpoints.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_optional_user, require_seller
from app.config.database import get_db
from app.models.user import User
from app.repositories.product_repository import ProductRepository
from app.schemas.common import MessageResponse, PaginatedResponse, PaginationParams
from app.schemas.product import ProductCreate, ProductListResponse, ProductResponse, ProductUpdate
from app.services.product_service import ProductService

router = APIRouter()


def get_product_service(db: AsyncSession = Depends(get_db)) -> ProductService:
    """Get product service dependency."""
    return ProductService(ProductRepository(db))


@router.get("", response_model=PaginatedResponse[ProductListResponse])
async def list_products(
    pagination: PaginationParams = Depends(),
    category_id: Optional[UUID] = None,
    brand: Optional[str] = None,
    is_local: Optional[bool] = None,
    product_service: ProductService = Depends(get_product_service),
) -> PaginatedResponse[ProductListResponse]:
    """List products with pagination and filters."""
    filters = {}
    if category_id:
        filters['category_id'] = category_id
    if brand:
        filters['brand'] = brand
    if is_local is not None:
        filters['is_local_product'] = is_local
    filters['is_active'] = True

    products = await product_service.get_multi(
        skip=pagination.skip,
        limit=pagination.limit,
        **filters
    )
    total = await product_service.repository.count(filters)

    items = [ProductListResponse.model_validate(p) for p in products]
    return PaginatedResponse.create(items, total, pagination.page, pagination.page_size)


@router.get("/search", response_model=List[ProductListResponse])
async def search_products(
    q: str = Query(..., min_length=2),
    category_id: Optional[UUID] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    brand: Optional[str] = None,
    is_local: Optional[bool] = None,
    limit: int = Query(20, le=100),
    product_service: ProductService = Depends(get_product_service),
) -> List[ProductListResponse]:
    """Search products."""
    products = await product_service.search(
        query=q,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        brand=brand,
        is_local=is_local,
        limit=limit,
    )
    return [ProductListResponse.model_validate(p) for p in products]


@router.get("/featured", response_model=List[ProductListResponse])
async def get_featured_products(
    limit: int = Query(10, le=50),
    product_service: ProductService = Depends(get_product_service),
) -> List[ProductListResponse]:
    """Get featured products."""
    products = await product_service.get_featured(limit)
    return [ProductListResponse.model_validate(p) for p in products]


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: UUID,
    current_user: Optional[User] = Depends(get_optional_user),
    product_service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    """Get product details."""
    product = await product_service.get(product_id)
    if not product:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Product not found")

    # Track view
    user_id = current_user.id if current_user else None
    await product_service.track_view(product_id, user_id)

    return ProductResponse.model_validate(product)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    current_user: User = Depends(require_seller),
    product_service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    """Create new product (sellers only)."""
    product = await product_service.create(product_in)
    return ProductResponse.model_validate(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: UUID,
    product_in: ProductUpdate,
    current_user: User = Depends(require_seller),
    product_service: ProductService = Depends(get_product_service),
) -> ProductResponse:
    """Update product (sellers only)."""
    product = await product_service.update(product_id, product_in)
    if not product:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Product not found")
    return ProductResponse.model_validate(product)


@router.delete("/{product_id}", response_model=MessageResponse)
async def delete_product(
    product_id: UUID,
    current_user: User = Depends(require_seller),
    product_service: ProductService = Depends(get_product_service),
) -> MessageResponse:
    """Delete product (sellers only)."""
    success = await product_service.delete(product_id)
    if not success:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Product not found")
    return MessageResponse(message="Product deleted successfully")
