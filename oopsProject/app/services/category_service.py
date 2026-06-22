"""
Category service for category management business logic.
"""
from typing import List, Optional
from uuid import UUID

from app.core.base_classes import BaseService
from app.models.category import Category
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.utils.helpers import slugify
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CategoryService(BaseService[Category, CategoryCreate, CategoryUpdate]):
    """Category service with business logic."""

    def __init__(self, repository: CategoryRepository) -> None:
        """
        Initialize category service.

        Args:
            repository: Category repository instance
        """
        super().__init__(repository)
        self.repository = repository

    async def create(self, obj_in: CategoryCreate) -> Category:
        """Create a new category."""
        # Generate slug
        slug = slugify(obj_in.name)

        # Ensure unique slug
        existing = await self.repository.get_by_slug(slug)
        if existing:
            from app.utils.helpers import generate_random_string
            slug = f"{slug}-{generate_random_string(4).lower()}"

        category_data = obj_in.model_dump()
        category_data['slug'] = slug

        category = await self.repository.create(category_data)
        logger.info(f"Category created: {category.name} (id={category.id})")

        return category

    async def get(self, id: UUID) -> Optional[Category]:
        """Get category by ID."""
        return await self.repository.get(id)

    async def get_by_slug(self, slug: str) -> Optional[Category]:
        """Get category by slug."""
        return await self.repository.get_by_slug(slug)

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[Category]:
        """Get multiple categories."""
        return await self.repository.get_multi(skip=skip, limit=limit, filters=filters)

    async def get_root_categories(self) -> List[Category]:
        """Get root categories."""
        return await self.repository.get_root_categories()

    async def get_subcategories(self, parent_id: UUID) -> List[Category]:
        """Get subcategories."""
        return await self.repository.get_subcategories(str(parent_id))

    async def get_featured(self) -> List[Category]:
        """Get featured categories."""
        return await self.repository.get_featured()

    async def update(self, id: UUID, obj_in: CategoryUpdate) -> Optional[Category]:
        """Update category."""
        update_data = obj_in.model_dump(exclude_unset=True)

        if 'name' in update_data:
            update_data['slug'] = slugify(update_data['name'])

        category = await self.repository.update(id, update_data)

        if category:
            logger.info(f"Category updated: {category.name} (id={category.id})")

        return category

    async def delete(self, id: UUID) -> bool:
        """Delete category."""
        return await self.repository.delete(id)
