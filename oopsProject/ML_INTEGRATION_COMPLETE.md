# sMart ML Integration - Complete! 🎉

## Overview

The ML recommendation and semantic search systems are now fully integrated into your sMart backend. Here's what has been implemented:

---

## 🤖 What's New

### 1. **Recommendation API Endpoints** ✅

Three new endpoints have been added for ML-powered recommendations:

#### **GET /api/v1/recommendations/for-you**
- **Description**: Personalized product recommendations for logged-in users
- **Authentication**: Required (JWT token)
- **Algorithm**: Collaborative Filtering
- **Parameters**:
  - `top_n` (query param, default=10): Number of recommendations
- **Response**: List of recommended products with scores

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/recommendations/for-you?top_n=10" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Example Response:**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "recommendations": [
    {
      "product_id": "456e7890-e89b-12d3-a456-426614174001",
      "score": 0.92,
      "product": {
        "id": "456e7890-e89b-12d3-a456-426614174001",
        "name": "Apple iPhone 14 Pro",
        "price": 129900.0,
        "brand": "Apple",
        "image_url": "https://..."
      }
    }
  ],
  "total": 10,
  "algorithm": "collaborative_filtering"
}
```

#### **GET /api/v1/recommendations/similar/{product_id}**
- **Description**: Find products similar to a given product
- **Authentication**: Optional
- **Algorithm**: Semantic Search (NLP-based)
- **Parameters**:
  - `product_id` (path param): UUID of the product
  - `top_n` (query param, default=10): Number of similar products
- **Response**: List of similar products with similarity scores

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/v1/recommendations/similar/456e7890-e89b-12d3-a456-426614174001?top_n=5"
```

#### **GET /api/v1/recommendations/trending**
- **Description**: Get trending products
- **Authentication**: Optional
- **Parameters**:
  - `top_n` (query param, default=10): Number of products
  - `category_id` (query param, optional): Filter by category
- **Response**: List of trending products

---

### 2. **Enhanced Product Search** ✅

The existing product search endpoint has been upgraded with **semantic search capabilities**:

#### **GET /api/v1/products/search**
- **Now uses**: ML-powered semantic search (NLP)
- **Fallback**: Traditional database search if ML model not available
- **Benefits**:
  - Understands query intent and meaning
  - Handles typos and synonyms
  - Returns more relevant results

**Example:**
```bash
# Traditional search: "laptop for coding"
# Semantic search finds: "MacBook Pro for developers", "ThinkPad for programming"

curl -X GET "http://localhost:8000/api/v1/products/search?q=laptop%20for%20coding&limit=10"
```

---

## 📁 New Files Created

### API Layer
- **`app/api/v1/recommendations.py`**: Recommendation endpoints
- **`app/schemas/recommendation.py`**: Pydantic schemas for recommendations

### Service Layer
- **`app/services/recommendation_service.py`**: Business logic for recommendations
- **Enhanced `app/services/product_service.py`**: Added semantic search integration

### ML Models (Already Existed)
- **`app/ml/recommendation/collaborative_filter.py`**: Collaborative filtering model
- **`app/ml/search/semantic_search.py`**: Semantic search engine

---

## 🏗️ Architecture

### Recommendation Service Flow

```
User Request → API Endpoint → Recommendation Service → ML Model → Database → Response
```

1. **User requests recommendations** via API
2. **Recommendation service** checks if ML model is loaded
3. **ML model** generates recommendations
4. **Service** fetches product details from database
5. **API** returns formatted response

### Semantic Search Flow

```
Search Query → Product Service → Semantic Search Model → Product IDs → Filter & Fetch → Results
```

1. **User searches** for products
2. **Product service** attempts semantic search first
3. **Semantic model** finds relevant products using NLP
4. **Service** applies filters (price, category, etc.)
5. **Fallback** to database search if ML model unavailable

---

## 🚀 How to Use

### Step 1: Train ML Models

Before using the recommendation features, you need to train the ML models:

```bash
# 1. Generate mock data (if not already done)
python scripts/generate_mock_data.py

# 2. Train all ML models
python scripts/train_ml_models.py
```

This will create:
- `ml_models/collaborative_recommender.joblib` (10-50 MB)
- `ml_models/semantic_search.joblib` (50-200 MB)

### Step 2: Start the Application

```bash
uvicorn app.main:app --reload
```

### Step 3: Test the Endpoints

Visit: **http://localhost:8000/docs**

You'll see new endpoints:
- **Recommendations** section with 3 new endpoints
- **Products** → `/search` now uses semantic search

### Step 4: Try It Out

1. **Register/Login** to get a JWT token
2. **View some products** to create interactions
3. **Call `/recommendations/for-you`** to get personalized recommendations
4. **Search products** with natural language queries

---

## 🧪 Testing the ML Features

### Test Personalized Recommendations

```python
import requests

# Login first
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"username": "customer@example.com", "password": "password123"}
)
token = login_response.json()["access_token"]

# Get recommendations
recommendations = requests.get(
    "http://localhost:8000/api/v1/recommendations/for-you",
    headers={"Authorization": f"Bearer {token}"},
    params={"top_n": 10}
)

print(recommendations.json())
```

### Test Semantic Search

```python
# Search with natural language
search_results = requests.get(
    "http://localhost:8000/api/v1/products/search",
    params={"q": "smartphone with good camera", "limit": 10}
)

print(search_results.json())
```

### Test Similar Products

```python
# Get similar products
similar = requests.get(
    f"http://localhost:8000/api/v1/recommendations/similar/{product_id}",
    params={"top_n": 5}
)

print(similar.json())
```

---

## 🔧 Configuration

### ML Model Settings

Models are configured in `app/config/settings.py`:

```python
# ML Model Configuration
ML_MODEL_PATH: str = "ml_models"  # Directory for saved models
```

### Model Loading

Models are loaded **lazily** (on first use) to:
- Reduce startup time
- Save memory if not needed
- Allow graceful fallback if models missing

---

## 📊 How the ML Models Work

### 1. Collaborative Filtering (Recommendations)

**Algorithm**: Item-based collaborative filtering
**Training Data**: User interactions (views, cart adds, purchases)
**How it works**:
1. Creates user-item interaction matrix
2. Calculates similarity between items
3. Recommends items similar to what user liked

**Weights**:
- View: 1.0
- Add to Cart: 3.0
- Purchase: 5.0

### 2. Semantic Search (Product Discovery)

**Algorithm**: Sentence transformers (all-MiniLM-L6-v2)
**Training Data**: Product names, descriptions, brands
**How it works**:
1. Converts products to vector embeddings
2. Converts search query to embedding
3. Finds products with highest cosine similarity

**Benefits**:
- Understands synonyms: "laptop" ↔ "notebook"
- Handles typos: "iphone" ↔ "iphne"
- Context-aware: "phone for photography" → finds camera-focused phones

---

## 🎯 Use Cases

### E-commerce Frontend

**Homepage**:
```javascript
// Show personalized recommendations
GET /api/v1/recommendations/for-you?top_n=6
```

**Product Detail Page**:
```javascript
// Show similar products
GET /api/v1/recommendations/similar/{productId}?top_n=4
```

**Search Bar**:
```javascript
// Smart search with ML
GET /api/v1/products/search?q={userQuery}&limit=20
```

**Trending Section**:
```javascript
// Show trending products
GET /api/v1/recommendations/trending?top_n=10
```

---

## 🔄 Model Retraining

Models should be retrained periodically as new data comes in:

### Manual Retraining

```bash
# Retrain all models with latest data
python scripts/train_ml_models.py
```

### Automatic Retraining (Recommended)

Set up a cron job or Celery task:

```python
# In your Celery tasks
@celery_app.task
def retrain_ml_models():
    """Retrain ML models daily."""
    import subprocess
    subprocess.run(["python", "scripts/train_ml_models.py"])
```

**Recommended schedule**: Daily at 2 AM

---

## 📈 Performance

### Expected Response Times

- **Personalized Recommendations**: < 100ms
- **Semantic Search**: < 50ms
- **Similar Products**: < 80ms

### Memory Usage

- **Collaborative Filter Model**: 10-50 MB
- **Semantic Search Model**: 50-200 MB
- **Total ML Models**: 60-250 MB

### Scalability

For large catalogs (100k+ products):
- Consider using vector databases (Pinecone, Weaviate, Milvus)
- Implement caching for popular queries
- Use batch predictions

---

## 🛠️ Troubleshooting

### "Model not trained" Error

**Solution**: Run `python scripts/train_ml_models.py`

### Semantic Search Not Working

**Symptoms**: Search falls back to database
**Solution**:
1. Check if `ml_models/semantic_search.joblib` exists
2. Verify model loaded: Check logs for "Semantic search model loaded"
3. Retrain if corrupted

### No Recommendations for New Users

**Expected**: System returns popular items for cold start
**Solution**: Normal behavior. As user interacts, recommendations improve

### Import Errors

**Solution**: Install ML requirements:
```bash
pip install -r requirements/ml.txt
```

---

## ✅ Integration Checklist

- ✅ ML models created (collaborative filtering + semantic search)
- ✅ Recommendation service implemented
- ✅ Recommendation API endpoints created
- ✅ Semantic search integrated into product search
- ✅ Proper error handling and fallbacks
- ✅ Lazy loading of models
- ✅ API documentation (Swagger)
- ✅ Training scripts ready
- ✅ Mock data generation for testing

---

## 🎉 Next Steps

Now that ML is integrated, you can:

1. **Test the endpoints** in Swagger UI
2. **Build a frontend** that uses these recommendations
3. **Add more ML features**:
   - Demand forecasting
   - Dynamic pricing
   - Fraud detection
   - Customer segmentation
4. **Monitor performance** and retrain regularly
5. **Implement A/B testing** for recommendation algorithms

---

## 📚 Additional Resources

- **Training Guide**: `COMPLETE_DATA_ML_GUIDE.md`
- **API Docs**: http://localhost:8000/docs
- **Model Code**: `app/ml/`
- **Service Code**: `app/services/recommendation_service.py`

---

## 🙋 Need Help?

If you encounter issues:
1. Check the logs for errors
2. Verify models are trained
3. Test fallback mechanisms
4. Review the training guide

Your ML-powered e-commerce backend is ready to use! 🚀
