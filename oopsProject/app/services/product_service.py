"""
Product service for product management business logic.
"""
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from app.config.settings import get_settings
from app.core.base_classes import BaseService
from app.core.cache import cache_manager, CacheKeys
from app.core.exceptions import NotFoundError
from app.ml.search.semantic_search import SemanticSearchEngine
from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate
from app.utils.helpers import slugify
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class ProductService(BaseService[Product, ProductCreate, ProductUpdate]):
    """Product service with business logic."""

    def __init__(self, repository: ProductRepository) -> None:
        """
        Initialize product service.

        Args:
            repository: Product repository instance
        """
        super().__init__(repository)
        self.repository = repository
        self.semantic_search: Optional[SemanticSearchEngine] = None
        self._search_model_loaded = False

    async def create(self, obj_in: ProductCreate) -> Product:
        """
        Create a new product.

        Args:
            obj_in: Product creation data

        Returns:
            Created product instance
        """
        # Generate slug from name
        slug = slugify(obj_in.name)

        # Ensure unique slug
        existing = await self.repository.get_by_slug(slug)
        if existing:
            from app.utils.helpers import generate_random_string
            slug = f"{slug}-{generate_random_string(6).lower()}"

        # Prepare product data
        product_data = obj_in.model_dump()
        product_data['slug'] = slug

        # Set meta fields if not provided
        if not product_data.get('meta_title'):
            product_data['meta_title'] = obj_in.name
        if not product_data.get('meta_description'):
            product_data['meta_description'] = obj_in.short_description or obj_in.name

        # Create product
        product = await self.repository.create(product_data)
        logger.info(f"Product created: {product.name} (id={product.id})")

        # Invalidate related caches
        await cache_manager.delete_pattern("products:*")
        if product.category_id:
            await cache_manager.delete(CacheKeys.PRODUCT_CATEGORY.format(category_id=product.category_id))

        return product

    async def get(self, id: UUID) -> Optional[Product]:
        """Get product by ID with caching."""
        # Try to get from cache
        cache_key = CacheKeys.PRODUCT.format(id=id)
        cached_product = await cache_manager.get(cache_key)

        if cached_product:
            logger.debug(f"Product cache hit for {id}")
            return Product(**cached_product) if isinstance(cached_product, dict) else cached_product

        # Get from database
        product = await self.repository.get(id)

        # Cache the result (10 minutes)
        if product:
            await cache_manager.set(cache_key, product.__dict__, ttl=600)
            logger.debug(f"Product cached for {id}")

        return product

    async def get_by_slug(self, slug: str) -> Optional[Product]:
        """Get product by slug."""
        return await self.repository.get_by_slug(slug)

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[Product]:
        """Get multiple products with filters."""
        return await self.repository.get_multi(skip=skip, limit=limit, filters=filters)

    async def _load_semantic_search(self) -> None:
        """Load semantic search model if not already loaded."""
        if self._search_model_loaded:
            return

        try:
            search_path = Path(settings.ML_MODEL_PATH) / 'semantic_search.joblib'
            if search_path.exists():
                self.semantic_search = SemanticSearchEngine()
                await self.semantic_search.load(str(search_path))
                self._search_model_loaded = True
                logger.info("Semantic search model loaded")
            else:
                logger.warning(f"Semantic search model not found at {search_path}")
        except Exception as e:
            logger.error(f"Error loading semantic search model: {e}")

    async def search(
        self,
        query: str,
        category_id: Optional[UUID] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        brand: Optional[str] = None,
        is_local: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
        use_semantic_search: bool = True,
    ) -> List[Product]:
        """
        Search products using semantic search or fallback to database search.

        Args:
            query: Search query
            category_id: Filter by category
            min_price: Minimum price filter
            max_price: Maximum price filter
            brand: Filter by brand
            is_local: Filter by local products
            skip: Skip N results
            limit: Limit results
            use_semantic_search: Whether to use ML-based semantic search

        Returns:
            List of matching products
        """
        # Try semantic search first if enabled and model is available
        if use_semantic_search:
            await self._load_semantic_search()

            if self.semantic_search and self.semantic_search.is_trained:
                try:
                    # Get product IDs from semantic search
                    search_results = await self.semantic_search.predict(query, top_n=limit * 2)
                    product_ids = [pid for pid, _ in search_results]

                    if product_ids:
                        # Fetch products and apply additional filters
                        products = []
                        for product_id in product_ids:
                            product = await self.repository.get(product_id)
                            if product and product.is_active:
                                # Apply filters
                                if category_id and product.category_id != category_id:
                                    continue
                                if brand and product.brand != brand:
                                    continue
                                if is_local is not None and product.is_local_product != is_local:
                                    continue
                                if min_price and product.price < min_price:
                                    continue
                                if max_price and product.price > max_price:
                                    continue
                                products.append(product)

                        # Apply pagination
                        return products[skip:skip + limit]

                except Exception as e:
                    logger.error(f"Semantic search failed, falling back to database search: {e}")

        # Fallback to database search
        return await self.repository.search(
            query=query,
            category_id=category_id,
            min_price=min_price,
            max_price=max_price,
            brand=brand,
            is_local=is_local,
            skip=skip,
            limit=limit,
        )

    async def update(self, id: UUID, obj_in: ProductUpdate) -> Optional[Product]:
        """Update product."""
        update_data = obj_in.model_dump(exclude_unset=True)

        # Update slug if name changed
        if 'name' in update_data:
            update_data['slug'] = slugify(update_data['name'])

        product = await self.repository.update(id, update_data)

        if product:
            logger.info(f"Product updated: {product.name} (id={product.id})")

            # Invalidate caches
            await cache_manager.delete(CacheKeys.PRODUCT.format(id=id))
            await cache_manager.delete_pattern("products:*")
            if product.category_id:
                await cache_manager.delete(CacheKeys.PRODUCT_CATEGORY.format(category_id=product.category_id))

        return product

    async def delete(self, id: UUID) -> bool:
        """Soft delete product."""
        product = await self.repository.get(id)
        if not product:
            return False

        await self.repository.update(id, {'is_active': False})
        logger.info(f"Product deactivated: {product.name} (id={product.id})")

        # Invalidate caches
        await cache_manager.delete(CacheKeys.PRODUCT.format(id=id))
        await cache_manager.delete_pattern("products:*")
        if product.category_id:
            await cache_manager.delete(CacheKeys.PRODUCT_CATEGORY.format(category_id=product.category_id))

        return True

    async def get_featured(self, limit: int = 10) -> List[Product]:
        """Get featured products."""
        return await self.repository.get_featured(limit)

    async def track_view(self, product_id: UUID, user_id: Optional[UUID] = None) -> None:
        """Track product view."""
        await self.repository.increment_view_count(product_id)

        # TODO: Track user interaction for ML
        # if user_id:
        #     await track_interaction(user_id, product_id, InteractionType.VIEW)
