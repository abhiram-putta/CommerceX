"""
Semantic Search Engine using Sentence Transformers.
Enables natural language product search.
"""
import os
from typing import List, Optional, Dict
from uuid import UUID

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import joblib

from app.core.base_classes import BaseMLModel
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SemanticSearchEngine(BaseMLModel):
    """
    Semantic search using sentence transformers.
    Converts products and queries to embeddings for similarity search.
    """

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize semantic search engine.

        Args:
            model_name: Sentence transformer model name
        """
        super().__init__()
        self.model_name = model_name
        self.encoder: Optional[SentenceTransformer] = None
        self.product_embeddings: Dict[str, np.ndarray] = {}
        self.product_texts: Dict[str, str] = {}

    async def train(self, products: List[dict]) -> None:
        """
        Index products for semantic search.

        Args:
            products: List of product dicts with id, name, description
        """
        logger.info(f"Indexing {len(products)} products for semantic search")

        # Load sentence transformer model
        if self.encoder is None:
            self.encoder = SentenceTransformer(self.model_name)
            logger.info(f"Loaded model: {self.model_name}")

        # Create text representations
        texts = []
        product_ids = []

        for product in products:
            product_id = str(product['id'])
            text = f"{product['name']} {product.get('description', '')} {product.get('brand', '')}"
            texts.append(text)
            product_ids.append(product_id)
            self.product_texts[product_id] = text

        # Generate embeddings
        embeddings = self.encoder.encode(texts, show_progress_bar=True)

        # Store embeddings
        for product_id, embedding in zip(product_ids, embeddings):
            self.product_embeddings[product_id] = embedding

        self.is_trained = True
        logger.info(f"Indexed {len(self.product_embeddings)} products")

    async def predict(self, query: str, top_n: int = 20) -> List[tuple]:
        """
        Search products using semantic similarity.

        Args:
            query: Search query
            top_n: Number of results

        Returns:
            List of (product_id, similarity_score) tuples
        """
        if not self.is_trained or self.encoder is None:
            logger.warning("Model not trained")
            return []

        try:
            # Encode query
            query_embedding = self.encoder.encode([query])[0]

            # Calculate similarities
            similarities = []
            for product_id, product_embedding in self.product_embeddings.items():
                similarity = cosine_similarity(
                    [query_embedding],
                    [product_embedding]
                )[0][0]
                similarities.append((product_id, float(similarity)))

            # Sort by similarity and return top N
            similarities.sort(key=lambda x: x[1], reverse=True)
            results = similarities[:top_n]

            logger.info(f"Search query '{query}' returned {len(results)} results")
            return [(UUID(pid), score) for pid, score in results]

        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []

    async def save(self, path: str) -> None:
        """Save embeddings to disk."""
        model_data = {
            'product_embeddings': self.product_embeddings,
            'product_texts': self.product_texts,
            'model_name': self.model_name,
            'is_trained': self.is_trained,
        }
        joblib.dump(model_data, path)
        logger.info(f"Search index saved to {path}")

    async def load(self, path: str) -> None:
        """Load embeddings from disk."""
        if not os.path.exists(path):
            logger.warning(f"Index file not found: {path}")
            return

        model_data = joblib.load(path)
        self.product_embeddings = model_data['product_embeddings']
        self.product_texts = model_data['product_texts']
        self.model_name = model_data['model_name']
        self.is_trained = model_data['is_trained']

        # Load encoder
        self.encoder = SentenceTransformer(self.model_name)
        logger.info(f"Search index loaded from {path}")

    def evaluate(self, test_data: List[dict]) -> dict:
        """Evaluate search quality."""
        return {
            'num_products_indexed': len(self.product_embeddings),
            'model_name': self.model_name,
            'is_trained': self.is_trained,
        }
