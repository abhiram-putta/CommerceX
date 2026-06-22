# sMart Backend - ML-Powered E-commerce Platform

A production-ready, ML-powered e-commerce backend platform built with FastAPI, connecting Customers, Retailers, and Wholesalers.

## 🚀 Features

### ✅ Implemented Core Features

- **Authentication & Authorization**
  - JWT-based authentication with refresh tokens
  - Role-based access control (Customer, Seller, Admin)
  - User registration and login
  - Password hashing with bcrypt

- **Product Management**
  - Complete CRUD operations
  - Category hierarchy
  - Product search with ML semantic search
  - Product filtering (category, brand, price, local)
  - Featured products
  - Stock quantity tracking

- **Shopping Cart**
  - Add/update/remove items
  - Real-time stock validation
  - Automatic quantity updates
  - Cart count and price calculations
  - Multi-seller support

- **Wishlist**
  - Add/remove products from wishlist
  - Check product in wishlist
  - Clear wishlist
  - Wishlist count

- **Order Management**
  - Complete order lifecycle (Pending → Delivered)
  - Order placement and tracking
  - Order cancellation with inventory rollback
  - Delivery address management
  - Order history with pagination
  - Order status timeline

- **Payment Processing**
  - Razorpay integration (UPI, Cards, Net Banking, Wallets)
  - Cash on Delivery (COD) support
  - Payment verification with signature validation
  - Refund processing
  - Transaction history
  - Payment status tracking

- **Review & Rating System**
  - 1-5 star ratings
  - Review title and comments
  - Verified purchase badges
  - Average rating calculation
  - Rating distribution analytics
  - One review per user per product

- **Real-Time Features (WebSocket)**
  - Live notifications
  - Real-time order tracking
  - Inventory updates
  - Connection pooling and management

- **Notifications**
  - In-app notifications
  - Order status updates
  - Payment notifications
  - Promotional messages
  - Unread count tracking

- **Inventory Management**
  - Stock tracking by seller
  - Low stock alerts
  - Inventory updates
  - Multi-location support

- **Analytics Dashboard**
  - Sales reports
  - Revenue charts
  - Top products
  - User analytics

### 🤖 ML Features (Implemented)

- **Recommendation Engine**
  - Collaborative filtering
  - Personalized recommendations
  - Similar product suggestions
  - Trending products
  - Cold start handling

- **Semantic Search**
  - NLP-powered search with sentence transformers
  - Query understanding
  - Typo tolerance

### 🛡️ Quality & Performance

- **Testing**
  - 42+ test cases covering critical features
  - Unit and integration tests
  - Pytest configuration with coverage reporting

- **Rate Limiting**
  - Redis-based rate limiting (60 req/min)
  - Per-user and per-IP tracking
  - Configurable limits

- **Security**
  - Security headers middleware
  - Input validation and sanitization
  - SQL injection protection (ORM)
  - XSS protection

- **Performance**
  - Database optimization strategies
  - Composite and partial indexes
  - Query optimization
  - Connection pooling
  - Async operations

## 🛠 Technology Stack

### Backend
- **Framework**: FastAPI (async, auto-documentation)
- **ORM**: SQLAlchemy 2.0 (async)
- **Database**: PostgreSQL 15+
- **Caching**: Redis 7+
- **Task Queue**: Celery with Redis broker
- **File Storage**: MinIO (S3-compatible)

### ML/AI Stack
- **scikit-learn**: Classical ML algorithms
- **sentence-transformers**: Semantic search
- **XGBoost/LightGBM**: Gradient boosting
- **Prophet/ARIMA**: Time-series forecasting
- **transformers**: NLP tasks

### Additional Tools
- **Authentication**: JWT (already implemented)
- **API Docs**: Swagger/OpenAPI (auto-generated)
- **Testing**: pytest with >80% coverage target
- **Validation**: Pydantic v2
- **Migrations**: Alembic
- **Logging**: structlog (JSON format)
- **Email**: SendGrid
- **SMS**: Twilio
- **Payment**: Razorpay

## 📁 Project Structure

```
smart_backend/
├── app/
│   ├── api/v1/              # API routes
│   ├── config/              # Configuration
│   ├── core/                # Core modules (security, exceptions, base classes)
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic schemas
│   ├── repositories/        # Data access layer
│   ├── services/            # Business logic layer
│   ├── ml/                  # Machine learning models
│   ├── tasks/               # Celery background tasks
│   ├── utils/               # Utilities
│   └── websockets/          # WebSocket handlers
├── tests/                   # Test suite
├── migrations/              # Alembic migrations
├── scripts/                 # Utility scripts
├── docker/                  # Docker configuration
├── ml_models/               # Saved ML models
└── requirements/            # Python dependencies
```

## 🚦 Quick Start

### Automated Setup (Recommended)

Run the automated setup script:

```bash
./setup.sh
```

This will automatically:
- Check Python version
- Create virtual environment
- Install all dependencies
- Set up environment variables
- Configure database
- Generate sample data
- Train ML models

### Manual Setup

For detailed manual setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Redis 6+

### Quick Manual Installation

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements/base.txt
pip install -r requirements/ml.txt
pip install -r requirements/dev.txt

# 3. Set up environment
cp .env.example .env
# Edit .env with your settings

# 4. Set up database
createdb smart_db
alembic upgrade head

# 5. Start the application
uvicorn app.main:app --reload
```

**Access the API**: http://localhost:8000/docs

## 📚 Documentation

### API Documentation

Once the application is running, access the interactive API documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Project Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete setup and installation guide
- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Comprehensive API reference with examples
- **[DATABASE_OPTIMIZATION.md](DATABASE_OPTIMIZATION.md)** - Database optimization strategies
- **[QUALITY_IMPROVEMENTS_SUMMARY.md](QUALITY_IMPROVEMENTS_SUMMARY.md)** - Quality enhancements and testing
- **[FINAL_PROJECT_STATUS.md](FINAL_PROJECT_STATUS.md)** - Complete feature list and project status

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication.

### Get Access Token

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

### Use Token in Requests

```bash
GET /api/v1/users/me
Authorization: Bearer <access_token>
```

## 🧪 Testing

Run tests with coverage:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api/test_users.py

# Run with markers
pytest -m unit          # Run only unit tests
pytest -m integration   # Run only integration tests
pytest -m ml            # Run only ML tests
```

## 🐳 Docker Deployment

### Build and run with Docker Compose

```bash
docker-compose up --build
```

This will start:
- FastAPI application
- PostgreSQL database
- Redis
- MinIO
- Celery worker
- Celery beat

## 📊 Database Schema

### Core Tables

- **users**: User accounts (customers, retailers, wholesalers)
- **user_profiles**: Extended user information
- **categories**: Product categories (hierarchical)
- **products**: Product catalog
- **inventory**: Stock management by owner
- **carts**: Shopping cart items
- **orders**: Order records
- **order_items**: Order line items
- **order_tracking**: Order status history
- **payments**: Payment transactions
- **reviews**: Product reviews and ratings
- **notifications**: User notifications
- **user_interactions**: ML tracking data
- **search_queries**: Search analytics

## 🤖 Machine Learning Models

### 1. Recommendation System

**Endpoints:**
- `GET /api/v1/recommendations/for-you` - Personalized recommendations
- `GET /api/v1/recommendations/similar/{id}` - Similar products
- `GET /api/v1/recommendations/bought-together/{id}` - Frequently bought together

**Models:**
- Collaborative filtering (user-based, item-based)
- Content-based filtering
- Hybrid approach

### 2. Smart Search

**Endpoints:**
- `GET /api/v1/search?q=query` - Semantic search
- `GET /api/v1/search/suggestions?q=query` - Auto-complete

**Features:**
- Semantic understanding using sentence transformers
- Typo tolerance
- Query expansion
- Personalized ranking

### 3. Demand Forecasting

**Endpoints:**
- `GET /api/v1/analytics/forecast/{product_id}` - Product demand forecast

**Models:**
- Time-series forecasting (Prophet/ARIMA)
- Seasonal pattern recognition

### 4. Dynamic Pricing

**Features:**
- Demand-based pricing
- Competitor analysis
- Time-based adjustments

### 5. Fraud Detection

**Features:**
- Real-time anomaly detection
- Behavioral pattern analysis
- Risk scoring

## 🔄 Background Tasks

Celery tasks handle:
- Email sending (order confirmations, shipping updates)
- SMS notifications (OTP, order updates)
- ML model training/retraining
- Analytics aggregation
- Stock alerts
- Report generation

## 📈 Monitoring and Logging

- **Logging**: Structured JSON logging with structlog
- **Metrics**: Prometheus metrics endpoints (planned)
- **Tracing**: Request ID tracking across services

## 🛡 Security Features

- JWT authentication with refresh tokens
- Password hashing (bcrypt)
- Input validation (Pydantic)
- SQL injection prevention (ORM)
- XSS protection
- Rate limiting
- CORS configuration

## 🌐 API Endpoints Overview

### Authentication
```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/verify-email
POST   /api/v1/auth/verify-phone
```

### Users
```
GET    /api/v1/users/me
PUT    /api/v1/users/me
DELETE /api/v1/users/me
```

### Products
```
GET    /api/v1/products
GET    /api/v1/products/{id}
POST   /api/v1/products
PUT    /api/v1/products/{id}
DELETE /api/v1/products/{id}
```

### Cart
```
GET    /api/v1/cart
POST   /api/v1/cart/items
PUT    /api/v1/cart/items/{id}
DELETE /api/v1/cart/items/{id}
```

### Orders
```
POST   /api/v1/orders
GET    /api/v1/orders
GET    /api/v1/orders/{id}
PUT    /api/v1/orders/{id}/cancel
GET    /api/v1/orders/{id}/tracking
```

### Payments
```
POST   /api/v1/payments/initiate
POST   /api/v1/payments/verify
```

### Recommendations
```
GET    /api/v1/recommendations/for-you
GET    /api/v1/recommendations/trending
GET    /api/v1/recommendations/similar/{id}
```

### Search
```
GET    /api/v1/search
GET    /api/v1/search/suggestions
```

### Analytics
```
GET    /api/v1/analytics/dashboard
GET    /api/v1/analytics/sales
GET    /api/v1/analytics/products/top
```

## 🚀 Performance Optimizations

- **Database**: Proper indexing on foreign keys and query fields
- **Caching**: Redis for frequently accessed data
- **Connection Pooling**: SQLAlchemy pool configuration
- **Async Operations**: FastAPI's async capabilities
- **Pagination**: Cursor-based pagination for large datasets

## 📝 Development Guidelines

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings (Google style)
- Run black for formatting: `black app/`
- Run isort for imports: `isort app/`
- Run mypy for type checking: `mypy app/`

### OOP Principles

- Repository pattern for data access
- Service layer for business logic
- Factory pattern for ML models
- Strategy pattern for algorithms
- Dependency injection

### Testing

- Aim for >80% code coverage
- Write unit tests for services and repositories
- Write integration tests for API endpoints
- Write ML model tests for accuracy

## 🤝 Contributing

This is an academic project. For contributions:

1. Create a feature branch
2. Write tests for new features
3. Ensure all tests pass
4. Update documentation
5. Submit a pull request

## 📄 License

This is an academic project.

## 👥 Team

sMart Development Team

## 📞 Support

For issues and questions, please create an issue in the repository.

---

**Note**: This is a comprehensive backend system designed for academic evaluation. It demonstrates advanced FastAPI development, OOP principles, ML integration, and production-ready code architecture.
