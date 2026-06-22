"""
Train all ML models with generated data.
This script trains recommendation and search models.
"""
import asyncio
import os
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import AsyncSessionLocal
from app.config.settings import get_settings
from app.models.interaction import UserInteraction
from app.models.product import Product
from app.ml.recommendation.collaborative_filter import CollaborativeRecommender
from app.ml.search.semantic_search import SemanticSearchEngine

settings = get_settings()


async def train_recommendation_model(db: AsyncSession):
    """Train collaborative filtering recommendation model."""
    print("🤖 Training Recommendation Model...")

    # Fetch user interactions
    result = await db.execute(select(UserInteraction))
    interactions = result.scalars().all()

    if not interactions:
        print("⚠️  No interactions found. Please generate mock data first.")
        return

    # Prepare training data
    training_data = []
    for interaction in interactions:
        # Assign scores based on interaction type
        score_map = {
            'view': 1.0,
            'add_to_cart': 3.0,
            'purchase': 5.0,
            'wishlist': 2.0,
        }
        score = score_map.get(interaction.interaction_type.value, 1.0)

        training_data.append({
            'user_id': str(interaction.user_id),
            'product_id': str(interaction.product_id),
            'score': score,
        })

    print(f"   Found {len(training_data)} interactions")

    # Train model
    model = CollaborativeRecommender()
    await model.train(training_data)

    # Save model
    model_path = Path(settings.ML_MODEL_PATH) / 'collaborative_recommender.joblib'
    model_path.parent.mkdir(parents=True, exist_ok=True)
    await model.save(str(model_path))

    # Evaluate
    metrics = model.evaluate([])
    print(f"   ✅ Model trained and saved")
    print(f"   - Users: {metrics['num_users']}")
    print(f"   - Products: {metrics['num_products']}")
    print(f"   - Sparsity: {metrics['sparsity']:.2%}")


async def train_search_model(db: AsyncSession):
    """Train semantic search model."""
    print("\n🔍 Training Semantic Search Model...")

    # Fetch all products
    result = await db.execute(select(Product).where(Product.is_active == True))
    products = result.scalars().all()

    if not products:
        print("⚠️  No products found. Please generate mock data first.")
        return

    # Prepare product data
    product_data = []
    for product in products:
        product_data.append({
            'id': str(product.id),
            'name': product.name,
            'description': product.description or '',
            'brand': product.brand or '',
        })

    print(f"   Found {len(product_data)} products")

    # Train/index model
    model = SemanticSearchEngine()
    await model.train(product_data)

    # Save model
    model_path = Path(settings.ML_MODEL_PATH) / 'semantic_search.joblib'
    model_path.parent.mkdir(parents=True, exist_ok=True)
    await model.save(str(model_path))

    # Test search
    test_results = await model.predict("smartphone", top_n=5)
    print(f"   ✅ Model trained and saved")
    print(f"   - Indexed products: {len(product_data)}")
    print(f"   - Test search 'smartphone': {len(test_results)} results")


async def test_recommendations(db: AsyncSession):
    """Test recommendation model."""
    print("\n🧪 Testing Recommendations...")

    # Load model
    model_path = Path(settings.ML_MODEL_PATH) / 'collaborative_recommender.joblib'
    if not model_path.exists():
        print("   ⚠️ Model not found. Train first.")
        return

    model = CollaborativeRecommender()
    await model.load(str(model_path))

    # Get a random user with interactions
    result = await db.execute(
        select(UserInteraction.user_id)
        .distinct()
        .limit(1)
    )
    user_id = result.scalar_one_or_none()

    if not user_id:
        print("   ⚠️ No users with interactions found.")
        return

    # Get recommendations
    recommendations = await model.predict(user_id, top_n=10)

    print(f"   Got {len(recommendations)} recommendations for user {user_id}")
    for product_id, score in recommendations[:5]:
        # Fetch product name
        result = await db.execute(
            select(Product.name).where(Product.id == product_id)
        )
        product_name = result.scalar_one_or_none()
        print(f"   - {product_name}: {score:.3f}")


async def test_search(db: AsyncSession):
    """Test semantic search."""
    print("\n🧪 Testing Semantic Search...")

    # Load model
    model_path = Path(settings.ML_MODEL_PATH) / 'semantic_search.joblib'
    if not model_path.exists():
        print("   ⚠️ Model not found. Train first.")
        return

    model = SemanticSearchEngine()
    await model.load(str(model_path))

    # Test queries
    test_queries = [
        "laptop for programming",
        "cotton shirt",
        "smartphone with good camera",
    ]

    for query in test_queries:
        results = await model.predict(query, top_n=3)
        print(f"\n   Query: '{query}'")

        for product_id, score in results:
            # Fetch product name
            result = await db.execute(
                select(Product.name).where(Product.id == product_id)
            )
            product_name = result.scalar_one_or_none()
            print(f"   - {product_name}: {score:.3f}")


async def main():
    """Main training function."""
    print("=" * 60)
    print("🚀 sMart ML Model Training")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        # Train models
        await train_recommendation_model(db)
        await train_search_model(db)

        # Test models
        await test_recommendations(db)
        await test_search(db)

    print("\n" + "=" * 60)
    print("✅ All ML models trained successfully!")
    print("=" * 60)
    print("\n📝 Models saved in:", settings.ML_MODEL_PATH)
    print("   - collaborative_recommender.joblib")
    print("   - semantic_search.joblib")
    print("\n🎯 You can now use the recommendation and search APIs!")


if __name__ == "__main__":
    asyncio.run(main())
