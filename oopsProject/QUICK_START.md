# Quick Start Guide

Get the sMart e-commerce backend running in 5 minutes!

## Prerequisites

- Python 3.10+
- PostgreSQL installed and running
- Redis installed and running

## 1. Automated Setup (Easiest)

```bash
cd /Users/shriyansp/Desktop/oopsProject
./setup.sh
```

That's it! The script will:
- Create virtual environment
- Install dependencies
- Set up database
- Generate sample data
- Train ML models

## 2. Manual Quick Start

### Step 1: Environment Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/base.txt
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and set these minimum values:
# SECRET_KEY=your-secret-key-here
# DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/smart_db
# REDIS_URL=redis://localhost:6379/0
```

### Step 3: Database Setup

```bash
# Create database
createdb smart_db

# Run migrations
alembic upgrade head
```

### Step 4: Start the Application

```bash
# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 5: Access the API

Open your browser to:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 3. Quick Test

### Register a User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "Test1234!",
    "full_name": "Test User",
    "role": "CUSTOMER"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=Test1234!"
```

Save the `access_token` from the response.

### Get Products

```bash
curl -X GET "http://localhost:8000/api/v1/products" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 4. With Sample Data

```bash
# Generate realistic product data
python scripts/realistic_product_data.py

# Generate mock data for testing
python scripts/generate_mock_data.py

# Train ML models
python scripts/train_ml_models.py
```

## 5. Using Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

## Common Commands

### Run Tests
```bash
pytest
pytest --cov=app
```

### Check API Health
```bash
curl http://localhost:8000/health
```

### View API Documentation
```bash
open http://localhost:8000/docs
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Troubleshooting

### Port 8000 already in use
```bash
# Find and kill process
lsof -i :8000
kill -9 <PID>
```

### Database connection error
```bash
# Check PostgreSQL is running
pg_isready

# Check database exists
psql -l | grep smart_db
```

### Redis connection error
```bash
# Check Redis is running
redis-cli ping  # Should return: PONG

# Start Redis
brew services start redis  # macOS
sudo service redis start   # Linux
```

### Import errors
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements/base.txt
```

## Next Steps

1. ✅ API is running at http://localhost:8000
2. ✅ Explore API docs at http://localhost:8000/docs
3. ✅ Test endpoints with the interactive UI
4. ✅ Check out the full API documentation in `API_DOCUMENTATION.md`
5. ✅ Build your frontend application!

## Quick API Examples

### Create Product (Seller)
```python
import requests

# Login as seller
login_response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    data={"username": "seller@example.com", "password": "password"}
)
token = login_response.json()["access_token"]

# Create product
headers = {"Authorization": f"Bearer {token}"}
product_data = {
    "name": "iPhone 14 Pro",
    "description": "Latest iPhone model",
    "category_id": "category-uuid-here",
    "base_price": 99999.00,
    "brand": "Apple",
    "unit_type": "piece"
}
response = requests.post(
    "http://localhost:8000/api/v1/products",
    json=product_data,
    headers=headers
)
print(response.json())
```

### Complete Purchase Flow
```python
import requests

base_url = "http://localhost:8000/api/v1"
token = "your-access-token"
headers = {"Authorization": f"Bearer {token}"}

# 1. Add to cart
requests.post(
    f"{base_url}/cart",
    json={"product_id": "product-uuid", "quantity": 2},
    headers=headers
)

# 2. View cart
cart = requests.get(f"{base_url}/cart", headers=headers).json()

# 3. Create order
order = requests.post(
    f"{base_url}/orders",
    json={
        "shipping_address": {
            "street": "123 Main St",
            "city": "Mumbai",
            "state": "Maharashtra",
            "postal_code": "400001",
            "country": "India"
        },
        "payment_method": "COD"
    },
    headers=headers
).json()

# 4. Track order
tracking = requests.get(
    f"{base_url}/orders/{order['id']}/track",
    headers=headers
).json()
print(tracking)
```

## WebSocket Example

```javascript
// Connect to notifications WebSocket
const token = "your-jwt-token";
const ws = new WebSocket(`ws://localhost:8000/ws/notifications?token=${token}`);

ws.onopen = () => {
  console.log('Connected to notifications');
};

ws.onmessage = (event) => {
  const notification = JSON.parse(event.data);
  console.log('New notification:', notification);
};

// Keep connection alive
setInterval(() => {
  ws.send('ping');
}, 30000);
```

## Development Workflow

```bash
# 1. Start development server with auto-reload
uvicorn app.main:app --reload

# 2. Make changes to code

# 3. Run tests
pytest

# 4. Check code format
black app/
isort app/

# 5. Commit changes
git add .
git commit -m "Your message"
```

## Production Deployment

```bash
# 1. Set production environment
export APP_ENV=production

# 2. Install production server
pip install gunicorn

# 3. Run with Gunicorn
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## Resources

- **Full Setup Guide**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **API Documentation**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Database Optimization**: [DATABASE_OPTIMIZATION.md](DATABASE_OPTIMIZATION.md)
- **Interactive API Docs**: http://localhost:8000/docs

## Support

Check the documentation files or create an issue if you encounter problems.

---

**You're ready to go! 🚀**
