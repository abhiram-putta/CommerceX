# sMart Backend - Implementation Guide

## 📋 Progress Tracker

### ✅ Completed (Phase 1 - Foundation)

1. **Project Structure** ✓
   - Complete directory organization
   - Configuration files (pytest, pyproject.toml, alembic.ini)
   - Docker setup (Dockerfile, docker-compose.yml)

2. **Configuration** ✓
   - `app/config/settings.py` - Pydantic Settings
   - `app/config/database.py` - SQLAlchemy async setup
   - `app/config/redis_client.py` - Redis caching

3. **Utilities** ✓
   - `app/utils/logger.py` - Structured logging
   - `app/utils/enums.py` - All enumerations
   - `app/utils/constants.py` - Application constants
   - `app/utils/helpers.py` - Helper functions
   - `app/utils/validators.py` - Custom validators

4. **Core Modules** ✓
   - `app/core/exceptions.py` - Exception hierarchy
   - `app/core/base_classes.py` - Abstract base classes

5. **Database Models** (All 14 models) ✓
   - `app/models/base.py` - Base model with UUID and timestamps
   - `app/models/user.py` - User and UserProfile
   - `app/models/category.py` - Category (hierarchical)
   - `app/models/product.py` - Product
   - `app/models/inventory.py` - Inventory and StockAlert
   - `app/models/relationship.py` - RetailerWholesalerLink
   - `app/models/cart.py` - Cart
   - `app/models/order.py` - Order, OrderItem, OrderTracking
   - `app/models/payment.py` - Payment
   - `app/models/review.py` - Review
   - `app/models/notification.py` - Notification
   - `app/models/interaction.py` - UserInteraction (ML)
   - `app/models/analytics.py` - SearchQuery

6. **Pydantic Schemas** ✓
   - `app/schemas/base.py` - Base schemas
   - `app/schemas/common.py` - Pagination, responses
   - `app/schemas/user.py` - User, auth, profile
   - `app/schemas/product.py` - Product CRUD
   - `app/schemas/category.py` - Category CRUD
   - `app/schemas/cart.py` - Cart operations
   - `app/schemas/order.py` - Order management
   - `app/schemas/payment.py` - Payment processing
   - `app/schemas/review.py` - Review system

---

## 🔨 Next Steps - Implementation Order

### Week 1: Core Backend (Days 1-7)

#### Day 1-2: Repository & Service Layer
- [ ] Create `app/repositories/base_repository.py` (concrete implementation)
- [ ] Create `app/services/base_service.py` (concrete implementation)
- [ ] Implement `UserRepository` and `UserService`
- [ ] Implement `ProductRepository` and `ProductService`
- [ ] Implement `CategoryRepository` and `CategoryService`

#### Day 3: Authentication & Security
- [ ] Create `app/core/security.py` - JWT integration
  - Password hashing (bcrypt)
  - Token generation and validation
  - Get current user dependency
- [ ] Create `app/core/dependencies.py`
  - Database dependency
  - Current user dependency
  - Role-based permissions
- [ ] Create `app/core/middleware.py`
  - Request logging
  - Error handling
  - CORS

#### Day 4: Main Application & API Setup
- [ ] Create `app/main.py` - FastAPI app initialization
- [ ] Create `app/api/__init__.py`
- [ ] Create `app/api/deps.py` - API dependencies
- [ ] Create `app/api/v1/__init__.py`
- [ ] Create `app/api/v1/router.py` - Main router

#### Day 5: Core API Endpoints
- [ ] `app/api/v1/auth.py` - Authentication endpoints
  - POST /register
  - POST /login
  - POST /refresh
  - POST /verify-email
  - POST /verify-phone
  - POST /forgot-password
  - POST /reset-password

- [ ] `app/api/v1/users.py` - User management
  - GET /users/me
  - PUT /users/me
  - DELETE /users/me
  - PUT /users/me/preferences

#### Day 6-7: Product & Cart Management
- [ ] `app/repositories/product_repository.py`
- [ ] `app/services/product_service.py`
- [ ] `app/api/v1/products.py`
  - GET /products (with filters, pagination)
  - GET /products/{id}
  - POST /products (retailers/wholesalers)
  - PUT /products/{id}
  - DELETE /products/{id}

- [ ] `app/repositories/cart_repository.py`
- [ ] `app/services/cart_service.py`
- [ ] `app/api/v1/cart.py`
  - GET /cart
  - POST /cart/items
  - PUT /cart/items/{id}
  - DELETE /cart/items/{id}
  - DELETE /cart/clear

---

### Week 2: Orders, Payments & ML Features (Days 8-14)

#### Day 8-9: Order Management
- [ ] `app/repositories/order_repository.py`
- [ ] `app/services/order_service.py`
- [ ] `app/api/v1/orders.py`
  - POST /orders (place order)
  - GET /orders
  - GET /orders/{id}
  - PUT /orders/{id}/cancel
  - GET /orders/{id}/tracking
  - PUT /orders/{id}/status (sellers)

#### Day 10: Payment Integration
- [ ] `app/services/payment_service.py` - Razorpay integration
- [ ] `app/api/v1/payments.py`
  - POST /payments/initiate
  - POST /payments/verify
  - POST /payments/webhook
  - POST /payments/refund

#### Day 11-12: ML - Recommendation System
- [ ] `app/ml/base_model.py` - Base ML model implementation
- [ ] `app/ml/recommendation/collaborative_filter.py`
  - User-based collaborative filtering
  - Item-based collaborative filtering
  - Matrix factorization (SVD/ALS)
- [ ] `app/ml/recommendation/content_based.py`
  - Product similarity
  - Feature extraction
- [ ] `app/ml/recommendation/hybrid_recommender.py`
  - Combine collaborative + content-based
- [ ] `app/services/recommendation_service.py`
- [ ] `app/api/v1/recommendations.py`
  - GET /recommendations/for-you
  - GET /recommendations/trending
  - GET /recommendations/similar/{id}

#### Day 13: ML - Semantic Search
- [ ] `app/ml/search/semantic_search.py`
  - Sentence transformer integration
  - Vector embeddings
  - Similarity search
- [ ] `app/ml/search/query_expander.py`
  - Synonym expansion
  - Spell correction
- [ ] `app/services/search_service.py`
- [ ] `app/api/v1/search.py`
  - GET /search
  - GET /search/suggestions

#### Day 14: ML - Other Models (Basic Implementation)
- [ ] `app/ml/forecasting/demand_forecaster.py` - Prophet/ARIMA
- [ ] `app/ml/pricing/dynamic_pricing.py` - XGBoost
- [ ] `app/ml/fraud/anomaly_detector.py` - Isolation Forest
- [ ] `app/ml/personalization/user_segmentation.py` - K-Means

---

### Week 3: Advanced Features & Testing (Days 15-21)

#### Day 15: Background Tasks (Celery)
- [ ] `app/tasks/celery_app.py` - Celery configuration
- [ ] `app/tasks/email_tasks.py` - Email sending
- [ ] `app/tasks/notification_tasks.py` - Notifications
- [ ] `app/tasks/ml_training_tasks.py` - ML model training
- [ ] `app/tasks/analytics_tasks.py` - Analytics aggregation

#### Day 16: Third-Party Integrations
- [ ] `app/services/file_service.py` - MinIO/S3
- [ ] `app/services/email_service.py` - SendGrid
- [ ] `app/services/sms_service.py` - Twilio
- [ ] `app/services/notification_service.py`

#### Day 17: WebSocket Real-time Features
- [ ] `app/websockets/connection_manager.py`
- [ ] `app/websockets/order_tracking.py`
- [ ] `app/websockets/notifications.py`
- [ ] Add WebSocket endpoints to main app

#### Day 18: Analytics & Reporting
- [ ] `app/services/analytics_service.py`
- [ ] `app/api/v1/analytics.py`
  - GET /analytics/dashboard
  - GET /analytics/sales
  - GET /analytics/inventory
  - GET /analytics/customers
  - GET /analytics/products/top

#### Day 19: Testing
- [ ] `tests/conftest.py` - Pytest fixtures
- [ ] `tests/test_api/test_auth.py`
- [ ] `tests/test_api/test_users.py`
- [ ] `tests/test_api/test_products.py`
- [ ] `tests/test_services/test_user_service.py`
- [ ] `tests/test_services/test_product_service.py`
- [ ] `tests/test_ml/test_recommendations.py`
- [ ] Run coverage: `pytest --cov=app --cov-report=html`

#### Day 20: Database & Scripts
- [ ] `migrations/env.py` - Alembic setup
- [ ] Create initial migration: `alembic revision --autogenerate -m "Initial schema"`
- [ ] `scripts/seed_database.py` - Database seeding
- [ ] `scripts/generate_mock_data.py` - Mock data generation
- [ ] `scripts/train_ml_models.py` - Initial ML training

#### Day 21: Documentation & Final Polish
- [ ] Generate Postman collection
- [ ] API documentation review
- [ ] Code cleanup and refactoring
- [ ] Performance testing
- [ ] Security audit

---

## 🚀 Quick Start Commands

### Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/base.txt
pip install -r requirements/ml.txt
pip install -r requirements/dev.txt

# Copy environment file
cp .env.example .env
# Edit .env with your configuration
```

### Docker
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

### Database
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# Seed database
python scripts/seed_database.py
```

### Run Application
```bash
# Development server
uvicorn app.main:app --reload

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Celery worker
celery -A app.tasks.celery_app worker --loglevel=info

# Celery beat
celery -A app.tasks.celery_app beat --loglevel=info
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api/test_users.py

# Run by marker
pytest -m unit
pytest -m integration
pytest -m ml
```

---

## 📝 Implementation Tips

### 1. Repository Pattern
```python
class UserRepository(BaseRepository[User]):
    async def create(self, obj_in: Dict[str, Any]) -> User:
        # Implementation
        pass

    async def get_by_email(self, email: str) -> Optional[User]:
        # Custom method
        pass
```

### 2. Service Layer
```python
class UserService(BaseService[User, UserCreate, UserUpdate]):
    async def create(self, obj_in: UserCreate) -> User:
        # Hash password
        # Call repository
        # Send verification email (Celery task)
        pass
```

### 3. API Endpoints
```python
@router.post("/", response_model=UserResponse)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    service = UserService(UserRepository(User, db))
    return await service.create(user_in)
```

### 4. ML Model Integration
```python
class CollaborativeRecommender(BaseMLModel):
    async def train(self, data: Any) -> None:
        # Train model
        await self.save(self.model_path)

    async def predict(self, user_id: UUID) -> List[UUID]:
        # Generate recommendations
        return product_ids
```

---

## 🎯 Critical Features to Implement

### Must-Have (Week 1-2)
1. ✅ User authentication (JWT)
2. ✅ Product CRUD with search
3. ✅ Cart management
4. ✅ Order placement
5. ✅ Payment integration (Razorpay)
6. ✅ Basic recommendation system

### Should-Have (Week 2-3)
7. Semantic search
8. Demand forecasting
9. Real-time notifications
10. Analytics dashboard
11. Review system
12. Email/SMS notifications

### Nice-to-Have (If Time Permits)
13. Dynamic pricing
14. Fraud detection
15. Advanced user segmentation
16. Social authentication
17. Invoice generation
18. Export reports

---

## 🔒 Security Checklist

- [ ] JWT token validation on protected routes
- [ ] Password hashing with bcrypt
- [ ] Input validation with Pydantic
- [ ] SQL injection prevention (ORM)
- [ ] XSS protection (sanitize inputs)
- [ ] Rate limiting
- [ ] CORS configuration
- [ ] Environment variable protection
- [ ] HTTPS in production
- [ ] Secure file uploads

---

## 📊 Testing Checklist

- [ ] Unit tests for services (>80% coverage)
- [ ] Unit tests for repositories
- [ ] Integration tests for API endpoints
- [ ] ML model accuracy tests
- [ ] Load testing (critical endpoints)
- [ ] Security testing
- [ ] E2E workflow tests

---

## 🎓 Academic Project Highlights

Make sure to showcase:
1. **OOP Principles** - Repository, Service, Factory patterns
2. **Async Python** - SQLAlchemy async, FastAPI async
3. **ML Integration** - Multiple models working together
4. **Real-time Features** - WebSockets
5. **Background Tasks** - Celery
6. **Clean Architecture** - Separation of concerns
7. **Testing** - High coverage
8. **Documentation** - Comprehensive README, API docs
9. **Scalability** - Docker, caching, async
10. **Production-Ready** - Error handling, logging, monitoring

---

**Remember**: This is a 2-3 week project. Focus on core features first, then add ML and advanced features. Quality over quantity!
