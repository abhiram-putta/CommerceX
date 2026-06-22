"""
Collaborative Filtering Recommendation System.
Uses user-item interactions to recommend products.
"""
import os
from typing import List, Optional
from uuid import UUID

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import joblib

from app.core.base_classes import BaseMLModel
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CollaborativeRecommender(BaseMLModel):
    """
    Collaborative filtering recommender using user-item matrix.
    Implements both user-based and item-based collaborative filtering.
    """

    def __init__(self, model_path: Optional[str] = None):
        """Initialize collaborative recommender."""
        super().__init__(model_path)
        self.user_item_matrix: Optional[pd.DataFrame] = None
        self.item_similarity_matrix: Optional[np.ndarray] = None
        self.user_similarity_matrix: Optional[np.ndarray] = None
        self.product_ids: List[UUID] = []
        self.user_ids: List[UUID] = []

    async def train(self, interactions: List[dict]) -> None:
        """
        Train collaborative filtering model.

        Args:
            interactions: List of user-product interactions
                         Each dict should have: user_id, product_id, score/rating
        """
        logger.info(f"Training collaborative filter with {len(interactions)} interactions")

        # Convert to DataFrame
        df = pd.DataFrame(interactions)

        # Create user-item matrix
        self.user_item_matrix = df.pivot_table(
            values='score',
            index='user_id',
            columns='product_id',
            fill_value=0.0
        )

        # Store IDs for lookup
        self.user_ids = list(self.user_item_matrix.index)
        self.product_ids = list(self.user_item_matrix.columns)

        # Calculate item-item similarity (for item-based CF)
        self.item_similarity_matrix = cosine_similarity(
            self.user_item_matrix.T  # Transpose for item similarity
        )

        # Calculate user-user similarity (for user-based CF)
        self.user_similarity_matrix = cosine_similarity(
            self.user_item_matrix
        )

        self.is_trained = True
        logger.info(f"Model trained: {len(self.user_ids)} users, {len(self.product_ids)} products")

    async def predict(self, user_id: UUID, top_n: int = 10) -> List[tuple]:
        """
        Get product recommendations for a user.

        Args:
            user_id: User UUID
            top_n: Number of recommendations

        Returns:
            List of (product_id, score) tuples
        """
        if not self.is_trained:
            logger.warning("Model not trained, returning empty recommendations")
            return []

        try:
            # Convert UUID to string for matrix lookup
            user_id_str = str(user_id)

            if user_id_str not in self.user_ids:
                # New user - return popular items
                return await self._get_popular_items(top_n)

            # Get user index
            user_idx = self.user_ids.index(user_id_str)

            # Get user's rated products
            user_ratings = self.user_item_matrix.iloc[user_idx]
            rated_products = user_ratings[user_ratings > 0].index.tolist()

            # Item-based collaborative filtering
            scores = {}
            for product_id in self.product_ids:
                if str(product_id) in rated_products:
                    continue  # Skip already rated products

                product_idx = self.product_ids.index(str(product_id))

                # Calculate score based on similar items
                weighted_sum = 0.0
                similarity_sum = 0.0

                for rated_product in rated_products:
                    rated_idx = self.product_ids.index(rated_product)
                    similarity = self.item_similarity_matrix[product_idx][rated_idx]

                    if similarity > 0:
                        weighted_sum += similarity * user_ratings[rated_product]
                        similarity_sum += similarity

                if similarity_sum > 0:
                    scores[product_id] = weighted_sum / similarity_sum

            # Sort by score and return top N
            recommendations = sorted(
                scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:top_n]

            return [(UUID(pid), score) for pid, score in recommendations]

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return await self._get_popular_items(top_n)

    async def _get_popular_items(self, top_n: int = 10) -> List[tuple]:
        """Get most popular items as fallback."""
        if self.user_item_matrix is None:
            return []

        # Calculate popularity (sum of interactions)
        popularity = self.user_item_matrix.sum(axis=0).sort_values(ascending=False)
        popular_items = popularity.head(top_n)

        return [(UUID(pid), score) for pid, score in popular_items.items()]

    async def save(self, path: str) -> None:
        """Save model to disk."""
        model_data = {
            'user_item_matrix': self.user_item_matrix,
            'item_similarity_matrix': self.item_similarity_matrix,
            'user_similarity_matrix': self.user_similarity_matrix,
            'product_ids': self.product_ids,
            'user_ids': self.user_ids,
            'is_trained': self.is_trained,
        }
        joblib.dump(model_data, path)
        logger.info(f"Model saved to {path}")

    async def load(self, path: str) -> None:
        """Load model from disk."""
        if not os.path.exists(path):
            logger.warning(f"Model file not found: {path}")
            return

        model_data = joblib.load(path)
        self.user_item_matrix = model_data['user_item_matrix']
        self.item_similarity_matrix = model_data['item_similarity_matrix']
        self.user_similarity_matrix = model_data['user_similarity_matrix']
        self.product_ids = model_data['product_ids']
        self.user_ids = model_data['user_ids']
        self.is_trained = model_data['is_trained']
        logger.info(f"Model loaded from {path}")

    def evaluate(self, test_data: List[dict]) -> dict:
        """Evaluate model performance."""
        # Simple evaluation - calculate coverage and diversity
        if not self.is_trained:
            return {'error': 'Model not trained'}

        return {
            'num_users': len(self.user_ids),
            'num_products': len(self.product_ids),
            'sparsity': 1 - (self.user_item_matrix > 0).sum().sum() / (
                len(self.user_ids) * len(self.product_ids)
            ),
            'is_trained': self.is_trained,
        }
