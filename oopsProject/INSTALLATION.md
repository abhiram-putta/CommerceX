# sMart E-Commerce Backend - Installation Guide

## 📋 Prerequisites

### System Requirements
- **Python**: 3.10 or higher
- **PostgreSQL**: 14 or higher
- **Redis**: 6 or higher
- **OS**: Linux, macOS, or Windows (WSL recommended)

### Check Your System
```bash
# Check Python version
python --version  # Should be 3.10+

# Check if pip is installed
pip --version

# Check PostgreSQL
psql --version  # Should be 14+

# Check Redis
redis-cli --version  # Should be 6+
```

---

## 🚀 Quick Installation (Recommended)

### Option 1: Automated Setup Script
```bash
# Navigate to project directory
cd oopsProject

# Run automated setup (installs everything)
chmod +x setup.sh
./setup.sh
```

The script will:
1. Check Python version
2. Create virtual environment
3. Install all dependencies
4. Set up environment variables
5. Create database
6. Run migrations
7. Offer to generate sample data

---

## 📦 Manual Installation

### Step 1: Clone or Download Project
```bash
# If using git
git clone <repository-url>
cd oopsProject

# Or if you already have it
cd oopsProject
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

**Option A: Full Installation (Recommended)**
```bash
# Install all dependencies (includes ML)
pip install -r requirements.txt
```

**Option B: Minimal Installation (No ML)**
```bash
# Install only core dependencies
pip install -r requirements-minimal.txt
```

**Option C: Selective Installation**
```bash
# Core features only
pip install -r requirements/base.txt

# Add ML features
pip install -r requirements/ml.txt

# Add development tools
pip install -r requirements/dev.txt
```

### Step 4: Install System Dependencies

**PostgreSQL**
```bash
# macOS
brew install postgresql@14
brew services start postgresql@14

# Linux (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install postgresql-14
sudo systemctl start postgresql

# Windows
# Download from: https://www.postgresql.org/download/windows/
```

**Redis**
```bash
# macOS
brew install redis
brew services start redis

# Linux (Ubuntu/Debian)
sudo apt-get install redis-server
sudo systemctl start redis

# Windows
# Use WSL or Docker
# Docker: docker run -d -p 6379:6379 redis:6-alpine
```

### Step 5: Configure Environment
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**Minimum Required Settings:**
```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/smart_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here-change-in-production

# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@smart.com
FRONTEND_URL=http://localhost:3000
```

### Step 6: Create Database
```bash
# Create database
createdb smart_db

# Verify
psql -l | grep smart_db
```

### Step 7: Run Migrations
```bash
# Run database migrations
alembic upgrade head

# Create search indexes (for full-text search)
psql -d smart_db -c "
CREATE INDEX IF NOT EXISTS idx_products_search ON products
USING GIN (
  to_tsvector('english',
    coalesce(name, '') || ' ' ||
    coalesce(short_description, '') || ' ' ||
    coalesce(brand, '')
  )
);
"
```

### Step 8: Start Application
```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Step 9: Verify Installation
```bash
# Check health endpoint
curl http://localhost:8000/health

# Access API documentation
open http://localhost:8000/docs
```

---

## 🐳 Docker Installation (Alternative)

### Using Docker Compose
```bash
# Start all services (PostgreSQL, Redis, App)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 🧪 Optional: Generate Sample Data

```bash
# Activate virtual environment first
source venv/bin/activate

# Generate sample data
python scripts/realistic_product_data.py

# Train ML models (optional)
python scripts/train_ml_models.py
```

---

## 📊 Verify Installation

### Test Core Features
```bash
# Test caching
curl http://localhost:8000/api/v1/products

# Test search
curl "http://localhost:8000/api/v1/search?q=laptop"

# Test autocomplete
curl "http://localhost:8000/api/v1/search/autocomplete?q=lap"

# Test admin dashboard
curl http://localhost:8000/api/v1/admin/dashboard/overview
```

### Access API Documentation
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## ⚙️ Configuration Options

### Environment Variables

**Required:**
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/smart_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-minimum-32-characters
```

**Email (Required for notifications):**
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@smart.com
FROM_NAME=sMart
FRONTEND_URL=http://localhost:3000
```

**Payment (Optional - for Razorpay):**
```env
RAZORPAY_KEY_ID=your_key_id
RAZORPAY_KEY_SECRET=your_key_secret
```

**Optional Services:**
```env
# Twilio (SMS)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token

# MinIO (Object Storage)
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# Google OAuth
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
```

---

## 🔧 Troubleshooting

### Common Issues

**1. Python Version Error**
```bash
# Install Python 3.10+
# macOS: brew install python@3.11
# Linux: sudo apt-get install python3.11
# Windows: Download from python.org
```

**2. PostgreSQL Connection Error**
```bash
# Check if PostgreSQL is running
# macOS: brew services list
# Linux: sudo systemctl status postgresql

# Start PostgreSQL
# macOS: brew services start postgresql@14
# Linux: sudo systemctl start postgresql
```

**3. Redis Connection Error**
```bash
# Check if Redis is running
redis-cli ping  # Should return "PONG"

# Start Redis
# macOS: brew services start redis
# Linux: sudo systemctl start redis
```

**4. Import Errors**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

**5. Database Migration Errors**
```bash
# Reset migrations (WARNING: loses data)
alembic downgrade base
alembic upgrade head

# Or drop and recreate database
dropdb smart_db
createdb smart_db
alembic upgrade head
```

**6. Permission Errors**
```bash
# Fix script permissions
chmod +x setup.sh

# Fix Python package permissions
pip install --user -r requirements.txt
```

---

## 🚀 Production Deployment

### Security Checklist
- [ ] Change `SECRET_KEY` to a secure random string
- [ ] Set `DEBUG=False` in production
- [ ] Use strong database passwords
- [ ] Enable SSL/TLS for PostgreSQL
- [ ] Use Redis password authentication
- [ ] Set up firewall rules
- [ ] Enable HTTPS with SSL certificates
- [ ] Configure CORS properly
- [ ] Set up monitoring and logging

### Performance Optimization
```bash
# Use gunicorn with uvicorn workers
pip install gunicorn

# Start with multiple workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

### Database Optimization
```sql
-- Add recommended indexes
CREATE INDEX CONCURRENTLY idx_products_category_active
ON products(category_id, is_active);

CREATE INDEX CONCURRENTLY idx_orders_customer_status_date
ON orders(customer_id, status, created_at DESC);

CREATE INDEX CONCURRENTLY idx_cart_user_created
ON cart(user_id, created_at DESC);

-- Analyze tables
ANALYZE products;
ANALYZE orders;
ANALYZE cart;
```

---

## 📚 Next Steps

After installation:

1. **Read Documentation**
   - [FEATURES_COMPLETE.md](FEATURES_COMPLETE.md) - All features overview
   - [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - API reference
   - [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick reference

2. **Test the API**
   - Visit http://localhost:8000/docs
   - Try the interactive API documentation
   - Test endpoints with sample data

3. **Develop Frontend**
   - Use the API documentation
   - Integrate with your React/Vue/Angular app
   - Use provided code examples

4. **Deploy to Production**
   - Read [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
   - Configure production environment
   - Set up monitoring

---

## 💡 Tips

### Development Tips
```bash
# Auto-reload on code changes
uvicorn app.main:app --reload

# Run with specific log level
uvicorn app.main:app --log-level debug

# Run on different port
uvicorn app.main:app --port 8080
```

### Database Tips
```bash
# View current migration
alembic current

# View migration history
alembic history

# Create new migration
alembic revision --autogenerate -m "Description"
```

### Testing Tips
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_search.py
```

---

## 📞 Support

### Getting Help

1. **Check Documentation**
   - [INDEX.md](INDEX.md) - Documentation index
   - [QUICK_START.md](QUICK_START.md) - Quick start guide

2. **Common Issues**
   - Review [Troubleshooting](#troubleshooting) section
   - Check logs: `tail -f logs/app.log`

3. **Database Issues**
   - Check [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
   - Review PostgreSQL logs

4. **Community**
   - Create GitHub issue
   - Check existing issues

---

## ✅ Installation Checklist

- [ ] Python 3.10+ installed
- [ ] PostgreSQL 14+ installed and running
- [ ] Redis 6+ installed and running
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (requirements.txt)
- [ ] Environment variables configured (.env)
- [ ] Database created (smart_db)
- [ ] Migrations run (alembic upgrade head)
- [ ] Search indexes created
- [ ] Application starts successfully
- [ ] Health check passes (http://localhost:8000/health)
- [ ] API docs accessible (http://localhost:8000/docs)

---

**Installation Complete! 🎉**

Your sMart e-commerce backend is ready to use!

Access the API documentation: http://localhost:8000/docs
