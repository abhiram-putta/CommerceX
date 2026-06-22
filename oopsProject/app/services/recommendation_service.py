"""
Recommendation service for ML-based product recommendations.
"""
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from app.config.settings import get_settings
from app.ml.recommendation.collaborative_filter import CollaborativeRecommender
from app.ml.search.semantic_search import SemanticSearchEngine
from app.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class RecommendationService:
    """
    Service for generating product recommendations using ML models.
    """

    def __init__(self, product_repository: ProductRepository):
        """
        Initialize recommendation service.

        Args:
            product_repository: Repository for product data access
        """
        self.product_repository = product_repository
        self.collaborative_model: Optional[CollaborativeRecommender] = None
        self.semantic_search: Optional[SemanticSearchEngine] = None
        self._models_loaded = False

    async def _load_models(self) -> None:
        """Load ML models if not already loaded."""
        if self._models_loaded:
            return

        try:
            # Load collaborative filtering model
            collab_path = Path(settings.ML_MODEL_PATH) / 'collaborative_recommender.joblib'
            if collab_path.exists():
                self.collaborative_model = CollaborativeRecommender()
                await self.collaborative_model.load(str(collab_path))
                logger.info("Collaborative filtering model loaded")
            else:
                logger.warning(f"Collaborative model not found at {collab_path}")

            # Load semantic search model
            search_path = Path(settings.ML_MODEL_PATH) / 'semantic_search.joblib'
            if search_path.exists():
                self.semantic_search = SemanticSearchEngine()
                await self.semantic_search.load(str(search_path))
                logger.info("Semantic search model loaded")
            else:
                logger.warning(f"Semantic search model not found at {search_path}")

            self._models_loaded = True

        except Exception as e:
            logger.error(f"Error loading ML models: {e}")
            raise

    async def get_personalized_recommendations(
        self,
        user_id: UUID,
        top_n: int = 10,
        exclude_product_ids: Optional[List[UUID]] = None
    ) -> List[tuple[UUID, float]]:
        """
        Get personalized product recommendations for a user.

        Args:
            user_id: User UUID
            top_n: Number of recommendations to return
            exclude_product_ids: Product IDs to exclude from recommendations

        Returns:
            List of (product_id, score) tuples
        """
        await self._load_models()

        if not self.collaborative_model or not self.collaborative_model.is_trained:
            logger.warning("Collaborative model not available, returning popular products")
            return await self._get_popular_products(top_n, exclude_product_ids)

        try:
            # Get recommendations from collaborative filtering
            recommendations = await self.collaborative_model.predict(user_id, top_n=top_n * 2)

            # Filter out excluded products
            if exclude_product_ids:
                exclude_set = set(str(pid) for pid in exclude_product_ids)
                recommendations = [
                    (pid, score) for pid, score in recommendations
                    if str(pid) not in exclude_set
                ]

            # Verify products exist and are active
            verified_recommendations = []
            for product_id, score in recommendations[:top_n]:
                product = await self.product_repository.get(product_id)
                if product and product.is_active:
                    verified_recommendations.append((product_id, score))

            return verified_recommendations

        except Exception as e:
            logger.error(f"Error generating personalized recommendations: {e}")
            return await self._get_popular_products(top_n, exclude_product_ids)

    async def get_similar_products(
        self,
        product_id: UUID,
        top_n: int = 10
    ) -> List[tuple[UUID, float]]:
        """
        Get products similar to a given product.

        Args:
            product_id: Product UUID
            top_n: Number of similar products to return

        Returns:
            List of (product_id, score) tuples
        """
        await self._load_models()

        # Get the source product
        product = await self.product_repository.get(product_id)
        if not product:
            logger.warning(f"Product {product_id} not found")
            return []

        if not self.semantic_search or not self.semantic_search.is_trained:
            logger.warning("Semantic search model not available")
            return await self._get_products_in_same_category(product_id, top_n)

        try:
            # Use semantic search to find similar products
            query = f"{product.name} {product.description or ''} {product.brand or ''}"
            similar = await self.semantic_search.predict(query, top_n=top_n + 1)

            # Filter out the source product itself
            similar = [(pid, score) for pid, score in similar if str(pid) != str(product_id)]

            return similar[:top_n]

        except Exception as e:
            logger.error(f"Error finding similar products: {e}")
            return await self._get_products_in_same_category(product_id, top_n)

    async def get_trending_products(
        self,
        top_n: int = 10,
        category_id: Optional[UUID] = None
    ) -> List[Product]:
        """
        Get trending products based on recent interactions.

        Args:
            top_n: Number of products to return
            category_id: Optional category filter

        Returns:
            List of Product objects
        """
        # For now, return popular products
        # In future, implement based on recent interactions weighted by time
        filters = {'is_active': True}
        if category_id:
            filters['category_id'] = category_id

        products = await self.product_repository.get_multi(limit=top_n, **filters)
        return products

    async def _get_popular_products(
        self,
        top_n: int = 10,
        exclude_product_ids: Optional[List[UUID]] = None
    ) -> List[tuple[UUID, float]]:
        """
        Fallback: Get popular products based on simple criteria.

        Args:
            top_n: Number of products to return
            exclude_product_ids: Product IDs to exclude

        Returns:
            List of (product_id, score) tuples
        """
        filters = {'is_active': True}
        products = await self.product_repository.get_multi(limit=top_n * 2, **filters)

        # Filter exclusions
        if exclude_product_ids:
            exclude_set = set(str(pid) for pid in exclude_product_ids)
            products = [p for p in products if str(p.id) not in exclude_set]

        # Return with dummy scores
        return [(p.id, 0.8) for p in products[:top_n]]

    async def _get_products_in_same_category(
        self,
        product_id: UUID,
        top_n: int = 10
    ) -> List[tuple[UUID, float]]:
        """
        Fallback: Get products in the same category.

        Args:
            product_id: Product UUID
            top_n: Number of products to return

        Returns:
            List of (product_id, score) tuples
        """
        product = await self.product_repository.get(product_id)
        if not product:
            return []

        filters = {
            'category_id': product.category_id,
            'is_active': True
        }
        similar_products = await self.product_repository.get_multi(limit=top_n + 1, **filters)

        # Filter out the source product
        similar_products = [p for p in similar_products if p.id != product_id]

        return [(p.id, 0.7) for p in similar_products[:top_n]]
