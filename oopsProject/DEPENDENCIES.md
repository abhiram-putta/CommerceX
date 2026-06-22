# Dependencies & Requirements

Complete list of all dependencies and system requirements for the sMart e-commerce backend.

## System Requirements

### Required

| Requirement | Minimum Version | Recommended Version | Purpose |
|------------|-----------------|---------------------|---------|
| Python | 3.10 | 3.11+ | Application runtime |
| PostgreSQL | 14 | 15+ | Primary database |
| Redis | 6.0 | 7.0+ | Caching & rate limiting |

### Optional (for full features)

| Service | Version | Purpose |
|---------|---------|---------|
| Docker | 20.10+ | Containerization |
| Docker Compose | 2.0+ | Multi-container orchestration |

## Python Dependencies

### Base Requirements (`requirements/base.txt`)

#### Web Framework
```
fastapi==0.109.0           # Modern async web framework
uvicorn[standard]==0.27.0  # ASGI server
python-multipart==0.0.6    # Form data parsing
```

#### Data Validation
```
pydantic[email]==2.5.3     # Data validation
pydantic-settings==2.1.0   # Settings management
email-validator==2.1.0     # Email validation
```

#### Database
```
sqlalchemy[asyncio]==2.0.25  # Async ORM
asyncpg==0.29.0              # PostgreSQL async driver
psycopg2-binary==2.9.9       # PostgreSQL sync driver
alembic==1.13.1              # Database migrations
```

#### Caching & Queue
```
redis==5.0.1               # Redis client
hiredis==2.3.2             # Redis protocol parser
celery==5.3.6              # Background tasks
flower==2.0.1              # Celery monitoring
```

#### Authentication & Security
```
python-jose[cryptography]==3.3.0  # JWT handling
passlib[bcrypt]==1.7.4            # Password hashing
bcrypt==4.1.2                      # Bcrypt algorithm
```

#### Third-Party Integrations
```
razorpay==1.4.1           # Payment gateway
sendgrid==6.11.0          # Email service
twilio==8.11.1            # SMS service
minio==7.2.3              # S3-compatible storage
google-auth==2.27.0       # Google OAuth
httpx==0.26.0             # HTTP client
```

#### Utilities
```
python-dotenv==1.0.0      # Environment variables
structlog==24.1.0         # Structured logging
python-json-logger==2.0.7 # JSON logging
phonenumbers==8.13.27     # Phone validation
python-dateutil==2.8.2    # Date utilities
pytz==2023.3.post1        # Timezone support
```

#### WebSocket
```
websockets==12.0          # WebSocket support
```

#### File Handling
```
Pillow==10.2.0            # Image processing
python-magic==0.4.27      # File type detection
```

### ML Requirements (`requirements/ml.txt`)

```
-r base.txt

# Core ML Libraries
numpy==1.24.3
pandas==2.0.3
scikit-learn==1.3.2

# NLP & Embeddings
sentence-transformers==2.2.2
transformers==4.35.2

# Additional ML
joblib==1.3.2             # Model serialization
scipy==1.11.4             # Scientific computing
```

### Development Requirements (`requirements/dev.txt`)

```
-r base.txt
-r ml.txt

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
pytest-mock==3.12.0
faker==22.5.1
factory-boy==3.3.0
httpx==0.26.0

# Code Quality
black==24.1.1             # Code formatting
isort==5.13.2             # Import sorting
flake8==7.0.0             # Linting
mypy==1.8.0               # Type checking
pylint==3.0.3             # Code analysis
autopep8==2.0.4           # Auto-formatting

# Pre-commit Hooks
pre-commit==3.6.0

# Documentation
mkdocs==1.5.3
mkdocs-material==9.5.6

# Development Tools
ipython==8.20.0
jupyter==1.0.0
watchfiles==0.21.0
```

## External Services

### Required for Full Functionality

#### 1. Razorpay (Payment Gateway)
- **Purpose**: Process payments (UPI, Cards, Net Banking, Wallets)
- **Signup**: https://razorpay.com
- **Environment Variables**:
  ```env
  RAZORPAY_KEY_ID=your_key_id
  RAZORPAY_KEY_SECRET=your_key_secret
  RAZORPAY_WEBHOOK_SECRET=your_webhook_secret
  ```
- **Required**: For payment features
- **Free Tier**: Yes (test mode)

#### 2. SendGrid (Email)
- **Purpose**: Send transactional emails
- **Signup**: https://sendgrid.com
- **Environment Variables**:
  ```env
  SENDGRID_API_KEY=your_api_key
  FROM_EMAIL=noreply@yourdomain.com
  FROM_NAME=YourApp
  ```
- **Required**: For email notifications (optional)
- **Free Tier**: Yes (100 emails/day)

#### 3. Twilio (SMS)
- **Purpose**: Send SMS notifications
- **Signup**: https://twilio.com
- **Environment Variables**:
  ```env
  TWILIO_ACCOUNT_SID=your_account_sid
  TWILIO_AUTH_TOKEN=your_auth_token
  TWILIO_PHONE_NUMBER=+1234567890
  ```
- **Required**: For SMS notifications (optional)
- **Free Tier**: Yes (trial credits)

### Optional Services

#### 4. Google OAuth
- **Purpose**: Social login
- **Setup**: Google Cloud Console
- **Environment Variables**:
  ```env
  GOOGLE_CLIENT_ID=your_client_id
  GOOGLE_CLIENT_SECRET=your_client_secret
  ```

#### 5. Facebook OAuth
- **Purpose**: Social login
- **Setup**: Facebook Developers
- **Environment Variables**:
  ```env
  FACEBOOK_APP_ID=your_app_id
  FACEBOOK_APP_SECRET=your_app_secret
  ```

## Installation Instructions

### 1. Install System Dependencies

#### macOS
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.11
brew install postgresql@15
brew install redis
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
sudo apt install postgresql-15 postgresql-contrib
sudo apt install redis-server
```

#### Windows
```bash
# Install via Chocolatey
choco install python --version=3.11
choco install postgresql15
choco install redis
```

### 2. Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements/base.txt       # Core dependencies
pip install -r requirements/ml.txt         # ML dependencies
pip install -r requirements/dev.txt        # Development dependencies
```

### 3. Verify Installation

```bash
# Check Python version
python --version  # Should be 3.10+

# Check PostgreSQL
psql --version

# Check Redis
redis-cli --version

# Check installed packages
pip list
```

## Dependency Management

### Update Dependencies

```bash
# Update all packages
pip install --upgrade -r requirements/base.txt

# Update specific package
pip install --upgrade fastapi
```

### Generate Requirements

```bash
# Generate from current environment
pip freeze > requirements-freeze.txt

# List outdated packages
pip list --outdated
```

### Security Audits

```bash
# Install safety
pip install safety

# Check for vulnerabilities
safety check

# Check with pip-audit
pip install pip-audit
pip-audit
```

## Docker Dependencies

All dependencies are pre-configured in `docker-compose.yml`:

```yaml
services:
  app:        # FastAPI application
  postgres:   # PostgreSQL 15
  redis:      # Redis 7
  minio:      # MinIO (S3-compatible)
  celery:     # Background tasks
  flower:     # Celery monitoring
```

Run with:
```bash
docker-compose up -d
```

## Version Compatibility Matrix

| Component | Compatible Versions |
|-----------|-------------------|
| Python | 3.10, 3.11, 3.12 |
| PostgreSQL | 14, 15, 16 |
| Redis | 6.0+, 7.0+ |
| FastAPI | 0.100+ |
| SQLAlchemy | 2.0+ |
| Pydantic | 2.0+ |

## Minimum vs Recommended Setup

### Minimum Setup (Development)
- Python 3.10
- PostgreSQL 14
- Redis 6.0
- 4GB RAM
- 10GB disk space

### Recommended Setup (Production)
- Python 3.11+
- PostgreSQL 15+
- Redis 7.0+
- 8GB+ RAM
- 50GB+ disk space
- Docker & Docker Compose
- Nginx (reverse proxy)
- SSL certificate

## Environment-Specific Dependencies

### Development Only
- pytest suite
- Code formatters (black, isort)
- Type checkers (mypy)
- Jupyter notebooks
- ipython

### Production Only
- gunicorn (production ASGI server)
- nginx (reverse proxy)
- supervisor (process manager)
- prometheus (monitoring)
- sentry (error tracking)

## Troubleshooting

### Common Issues

#### 1. PostgreSQL Connection Error
```bash
# Check PostgreSQL is running
pg_isready

# Start PostgreSQL
brew services start postgresql@15  # macOS
sudo service postgresql start       # Linux
```

#### 2. Redis Connection Error
```bash
# Check Redis is running
redis-cli ping  # Should return: PONG

# Start Redis
brew services start redis  # macOS
sudo service redis start   # Linux
```

#### 3. Python Module Not Found
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements/base.txt
```

#### 4. Compilation Errors (ML packages)
```bash
# Install build tools
# macOS
xcode-select --install

# Ubuntu
sudo apt install build-essential python3-dev

# Then reinstall
pip install -r requirements/ml.txt
```

## License Information

### Open Source Dependencies

All Python dependencies are open source:
- **MIT License**: FastAPI, Uvicorn, Pydantic, SQLAlchemy
- **BSD License**: Redis, NumPy, Pandas, scikit-learn
- **Apache 2.0**: Transformers, sentence-transformers

### Third-Party Services

Check individual service terms:
- Razorpay: Commercial license
- SendGrid: Commercial license
- Twilio: Commercial license

## Support

For dependency-related issues:
1. Check this document
2. Review `requirements/*.txt` files
3. Check package documentation
4. Create an issue on GitHub

---

**Last Updated**: 2024
**Total Dependencies**: ~60 packages
**Python Version**: 3.10+
