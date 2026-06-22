# Complete Setup Guide for sMart E-Commerce Backend

This guide will walk you through setting up and running the complete sMart e-commerce backend.

## Prerequisites

- Python 3.10 or higher
- PostgreSQL 14+
- Redis 6+
- Git

## Quick Start (Development)

### 1. Clone and Navigate

```bash
cd /Users/shriyansp/Desktop/oopsProject
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install all dependencies
pip install --upgrade pip
pip install -r requirements/base.txt
pip install -r requirements/ml.txt
pip install -r requirements/dev.txt
```

### 4. Set Up Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit .env file with your settings
nano .env  # or use your preferred editor
```

**Required Environment Variables:**

```env
# App Settings
APP_NAME=sMart Backend
APP_ENV=development
DEBUG=True
API_V1_PREFIX=/api/v1

# Security
SECRET_KEY=your-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/smart_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Razorpay (Optional for payments)
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_key_secret

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

### 5. Set Up Database

```bash
# Start PostgreSQL (if not running)
# macOS with Homebrew:
brew services start postgresql@14

# Create database
createdb smart_db

# Run migrations
alembic upgrade head
```

### 6. Start Redis

```bash
# macOS with Homebrew:
brew services start redis

# Or run in foreground:
redis-server
```

### 7. Generate Sample Data (Optional)

```bash
# Generate realistic product data
python scripts/realistic_product_data.py

# Generate mock data for testing
python scripts/generate_mock_data.py
```

### 8. Train ML Models (Optional)

```bash
# Train recommendation models
python scripts/train_ml_models.py
```

### 9. Run the Application

```bash
# Development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python directly
python app/main.py
```

### 10. Access the Application

- **API Documentation (Swagger)**: http://localhost:8000/docs
- **API Documentation (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Root**: http://localhost:8000

## Docker Setup (Recommended for Production)

### 1. Using Docker Compose

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 2. Individual Service Commands

```bash
# Start PostgreSQL
docker-compose up -d postgres

# Start Redis
docker-compose up -d redis

# Start application
docker-compose up -d app
```

## Testing

### Run Tests

```bash
# Install test dependencies (if not already installed)
pip install -r requirements/dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py

# Run tests by marker
pytest -m unit        # Unit tests only
pytest -m integration # Integration tests only

# View coverage report
open htmlcov/index.html
```

## Project Structure

```
oopsProject/
├── app/
│   ├── api/
│   │   └── v1/              # API endpoints
│   │       ├── auth.py
│   │       ├── products.py
│   │       ├── cart.py
│   │       ├── orders.py
│   │       ├── payments.py
│   │       ├── reviews.py
│   │       ├── wishlist.py
│   │       ├── notifications.py
│   │       ├── inventory.py
│   │       ├── analytics.py
│   │       ├── websocket.py
│   │       └── router.py
│   ├── core/                # Core functionality
│   │   ├── base_classes.py
│   │   ├── exceptions.py
│   │   ├── websocket.py
│   │   ├── rate_limiter.py
│   │   └── middleware.py
│   ├── models/              # Database models
│   ├── repositories/        # Data access layer
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   ├── utils/               # Utilities
│   ├── config/              # Configuration
│   └── main.py              # Application entry point
├── tests/                   # Test suite
├── scripts/                 # Utility scripts
├── migrations/              # Alembic migrations
├── ml_models/               # ML model storage
├── requirements/            # Dependencies
├── docker/                  # Docker configs
└── docs/                    # Documentation
```

## Available API Endpoints

### Authentication (4 endpoints)
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

### Products (6 endpoints)
- `GET /api/v1/products` - List products
- `GET /api/v1/products/{id}` - Get product
- `POST /api/v1/products` - Create product (seller)
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product
- `GET /api/v1/products/search` - Search products

### Cart (6 endpoints)
- `GET /api/v1/cart` - Get cart
- `POST /api/v1/cart` - Add to cart
- `PUT /api/v1/cart/{product_id}` - Update cart item
- `DELETE /api/v1/cart/{product_id}` - Remove from cart
- `DELETE /api/v1/cart` - Clear cart
- `GET /api/v1/cart/count` - Get cart count

### Wishlist (6 endpoints)
- `GET /api/v1/wishlist` - Get wishlist
- `POST /api/v1/wishlist` - Add to wishlist
- `DELETE /api/v1/wishlist/{product_id}` - Remove from wishlist
- `DELETE /api/v1/wishlist` - Clear wishlist
- `GET /api/v1/wishlist/count` - Get wishlist count
- `GET /api/v1/wishlist/check/{product_id}` - Check if in wishlist

### Orders (5 endpoints)
- `POST /api/v1/orders` - Create order
- `GET /api/v1/orders` - List orders
- `GET /api/v1/orders/{id}` - Get order
- `POST /api/v1/orders/{id}/cancel` - Cancel order
- `GET /api/v1/orders/{id}/track` - Track order

### Payments (6 endpoints)
- `POST /api/v1/payments/initiate` - Initiate payment
- `POST /api/v1/payments/verify` - Verify payment
- `POST /api/v1/payments/{id}/refund` - Process refund
- `POST /api/v1/payments/{order_id}/mark-cod-paid` - Mark COD as paid
- `GET /api/v1/payments/{order_id}` - Get payment details
- `GET /api/v1/payments/transaction-history` - Get payment history

### Reviews (7 endpoints)
- `POST /api/v1/reviews` - Create review
- `GET /api/v1/reviews/product/{product_id}` - Get product reviews
- `GET /api/v1/reviews/my-reviews` - Get user's reviews
- `PUT /api/v1/reviews/{id}` - Update review
- `DELETE /api/v1/reviews/{id}` - Delete review
- `POST /api/v1/reviews/{id}/helpful` - Mark review as helpful
- `GET /api/v1/reviews/{product_id}/stats` - Get review statistics

### WebSocket (3 endpoints)
- `WS /ws/notifications` - Real-time notifications
- `WS /ws/orders/{order_id}` - Order tracking
- `WS /ws/inventory` - Inventory updates

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
pg_isready

# Check database exists
psql -l | grep smart_db

# Recreate database if needed
dropdb smart_db
createdb smart_db
alembic upgrade head
```

### Redis Connection Issues

```bash
# Check Redis is running
redis-cli ping
# Should return: PONG

# Restart Redis
brew services restart redis
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Import Errors

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements/base.txt

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

### Migration Issues

```bash
# Reset migrations
alembic downgrade base
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "description"
```

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/new-feature
```

### 2. Make Changes

- Write code
- Write tests
- Update documentation

### 3. Run Tests

```bash
pytest
black app/  # Format code
isort app/  # Sort imports
```

### 4. Commit and Push

```bash
git add .
git commit -m "Add new feature"
git push origin feature/new-feature
```

## Production Deployment

### Environment Variables

Update `.env` for production:

```env
APP_ENV=production
DEBUG=False
SECRET_KEY=<strong-random-secret>
DATABASE_URL=<production-database-url>
REDIS_URL=<production-redis-url>
ALLOWED_ORIGINS=https://yourdomain.com
```

### Run with Gunicorn

```bash
pip install gunicorn

gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Using Docker in Production

```bash
# Build production image
docker build -f docker/Dockerfile.prod -t smart-backend:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  --env-file .env.production \
  --name smart-backend \
  smart-backend:latest
```

### Database Optimization

```sql
-- Apply indexes from DATABASE_OPTIMIZATION.md
-- Run as superuser

-- Example:
CREATE INDEX idx_products_category_active ON products(category_id, is_active);
CREATE INDEX idx_orders_customer_status_date ON orders(customer_id, status, created_at DESC);

-- Analyze tables
ANALYZE products;
ANALYZE orders;
```

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### WebSocket Status

```bash
curl http://localhost:8000/api/v1/ws/status
```

### Logs

```bash
# View application logs
tail -f logs/app.log

# Docker logs
docker-compose logs -f app
```

## Resources

- **API Documentation**: http://localhost:8000/docs
- **Database Optimization**: See `DATABASE_OPTIMIZATION.md`
- **API Reference**: See `API_DOCUMENTATION.md`
- **Quality Improvements**: See `QUALITY_IMPROVEMENTS_SUMMARY.md`

## Support

For issues or questions:
1. Check the documentation files in the project root
2. Review API docs at `/docs`
3. Check logs for errors
4. Create an issue on GitHub

## Next Steps

1. ✅ Install dependencies
2. ✅ Set up database
3. ✅ Configure environment variables
4. ✅ Run migrations
5. ✅ Start the application
6. ✅ Test endpoints at /docs
7. 🔄 Build frontend application
8. 🔄 Deploy to production

**Your sMart backend is ready to use! 🚀**
