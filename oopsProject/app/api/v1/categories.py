"""
Category management endpoints.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_seller
from app.config.database import get_db
from app.models.user import User
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.schemas.common import MessageResponse
from app.services.category_service import CategoryService

router = APIRouter()


def get_category_service(db: AsyncSession = Depends(get_db)) -> CategoryService:
    """Get category service dependency."""
    return CategoryService(CategoryRepository(db))


@router.get("", response_model=List[CategoryResponse])
async def list_categories(
    category_service: CategoryService = Depends(get_category_service),
) -> List[CategoryResponse]:
    """List all root categories."""
    categories = await category_service.get_root_categories()
    return [CategoryResponse.model_validate(c) for c in categories]


@router.get("/featured", response_model=List[CategoryResponse])
async def get_featured_categories(
    category_service: CategoryService = Depends(get_category_service),
) -> List[CategoryResponse]:
    """Get featured categories."""
    categories = await category_service.get_featured()
    return [CategoryResponse.model_validate(c) for c in categories]


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: UUID,
    category_service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    """Get category details."""
    category = await category_service.get(category_id)
    if not category:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Category not found")
    return CategoryResponse.model_validate(category)


@router.get("/{category_id}/subcategories", response_model=List[CategoryResponse])
async def get_subcategories(
    category_id: UUID,
    category_service: CategoryService = Depends(get_category_service),
) -> List[CategoryResponse]:
    """Get subcategories of a category."""
    subcategories = await category_service.get_subcategories(category_id)
    return [CategoryResponse.model_validate(c) for c in subcategories]


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_in: CategoryCreate,
    current_user: User = Depends(require_seller),
    category_service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    """Create new category (sellers only)."""
    category = await category_service.create(category_in)
    return CategoryResponse.model_validate(category)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    category_in: CategoryUpdate,
    current_user: User = Depends(require_seller),
    category_service: CategoryService = Depends(get_category_service),
) -> CategoryResponse:
    """Update category (sellers only)."""
    category = await category_service.update(category_id, category_in)
    if not category:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Category not found")
    return CategoryResponse.model_validate(category)


@router.delete("/{category_id}", response_model=MessageResponse)
async def delete_category(
    category_id: UUID,
    current_user: User = Depends(require_seller),
    category_service: CategoryService = Depends(get_category_service),
) -> MessageResponse:
    """Delete category (sellers only)."""
    success = await category_service.delete(category_id)
    if not success:
        from app.core.exceptions import NotFoundError
        raise NotFoundError("Category not found")
    return MessageResponse(message="Category deleted successfully")
