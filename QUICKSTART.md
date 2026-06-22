# sMart E-Commerce - Quick Start Guide

This is a complete e-commerce platform with a FastAPI backend and React frontend.

## 🚀 Quick Start

### Backend Setup

```bash
cd oopsProject

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env
# Edit .env and configure your database and other settings

# Run migrations
alembic upgrade head

# Start the backend server
uvicorn app.main:app --reload
```

Backend will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create environment file
copy .env.example .env

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## 📋 Features

### Implemented Features

✅ **Authentication & Authorization**
- User registration and login
- JWT-based authentication
- Role-based access control (Customer, Retailer, Wholesaler, Admin)
- Password reset functionality

✅ **Product Management**
- Product browsing with pagination
- Advanced search and filtering
- Product details with images
- Product reviews and ratings
- Featured products
- Category-based browsing

✅ **Shopping Experience**
- Shopping cart management
- Wishlist functionality
- Order placement
- Order tracking
- Order history

✅ **User Features**
- User profile management
- Notification center
- Review system
- Personalized recommendations

✅ **Admin Features**
- Admin dashboard with analytics
- Sales metrics
- Inventory management
- User management
- Order management

### Backend API Endpoints

**Authentication** (`/api/v1/auth`)
- POST `/register` - Register new user
- POST `/login` - User login
- POST `/refresh` - Refresh access token
- POST `/forgot-password` - Request password reset
- POST `/reset-password` - Reset password

**Products** (`/api/v1/products`)
- GET `/` - List products
- GET `/{id}` - Get product details
- GET `/search` - Search products
- GET `/featured` - Get featured products
- POST `/` - Create product (sellers)
- PUT `/{id}` - Update product (sellers)
- DELETE `/{id}` - Delete product (sellers)

**Cart** (`/api/v1/cart`)
- GET `/` - Get user cart
- POST `/` - Add item to cart
- PUT `/{item_id}` - Update cart item
- DELETE `/{item_id}` - Remove cart item
- DELETE `/` - Clear cart

**Orders** (`/api/v1/orders`)
- GET `/` - Get user orders
- GET `/{id}` - Get order details
- POST `/` - Create order
- POST `/{id}/cancel` - Cancel order
- GET `/{id}/tracking` - Get order tracking

**Reviews** (`/api/v1/reviews`)
- POST `/` - Create review
- GET `/product/{id}` - Get product reviews
- GET `/product/{id}/summary` - Get review summary
- PUT `/{id}` - Update review
- DELETE `/{id}` - Delete review

**Wishlist** (`/api/v1/wishlist`)
- GET `/` - Get wishlist
- POST `/` - Add to wishlist
- DELETE `/{product_id}` - Remove from wishlist
- GET `/count` - Get wishlist count

**Notifications** (`/api/v1/notifications`)
- GET `/` - Get notifications
- GET `/unread-count` - Get unread count
- PUT `/{id}/read` - Mark as read
- PUT `/mark-all-read` - Mark all as read

**Admin** (`/api/v1/admin`)
- GET `/dashboard/overview` - Dashboard overview
- GET `/dashboard/sales` - Sales metrics
- GET `/dashboard/revenue` - Revenue metrics
- GET `/dashboard/products` - Product metrics
- GET `/dashboard/orders` - Order metrics

## 🏗️ Architecture

### Backend (FastAPI + PostgreSQL)
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens
- **Caching**: Redis
- **Background Tasks**: Celery (configured)
- **ML Features**: Product recommendations, semantic search
- **API Documentation**: Auto-generated with OpenAPI/Swagger

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **Routing**: React Router
- **HTTP Client**: Axios
- **Forms**: React Hook Form with Zod validation
- **Icons**: Lucide React
- **Notifications**: React Hot Toast

## 📱 Pages & Routes

- `/` - Home page with featured products
- `/login` - User login
- `/register` - User registration
- `/products` - Product listing
- `/products/:id` - Product details
- `/cart` - Shopping cart
- `/wishlist` - Saved items
- `/orders` - Order history
- `/orders/:id` - Order details
- `/notifications` - Notification center
- `/profile` - User profile
- `/settings` - User settings

## 🔧 Configuration

### Backend Environment Variables (.env)

```env
# App
APP_NAME=sMart Backend
APP_ENV=development
DEBUG=True
API_V1_PREFIX=/api/v1

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/smart_db

# Redis
REDIS_URL=redis://localhost:6379/0

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend Environment Variables (.env)

```env
VITE_API_URL=http://localhost:8000/api/v1
```

## 🧪 Testing

### Test User Credentials

After seeding the database, you can use:
- Email: `customer@example.com`
- Password: `Customer@123`

Or register a new account at `/register`

## 📚 Documentation

- Backend API Docs: http://localhost:8000/docs
- Backend ReDoc: http://localhost:8000/redoc
- Frontend README: `frontend/README.md`
- Backend docs: `oopsProject/README.md` (if exists)

## 🛠️ Development

### Backend Development

```bash
# Run with auto-reload
uvicorn app.main:app --reload --port 8000

# Create new migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Frontend Development

```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## 🐛 Common Issues

### Backend Issues

1. **Database Connection Error**
   - Verify PostgreSQL is running
   - Check DATABASE_URL in .env
   - Ensure database exists

2. **Redis Connection Error**
   - Verify Redis is running
   - Check REDIS_URL in .env

3. **Import Errors**
   - Ensure virtual environment is activated
   - Run `pip install -r requirements.txt`

### Frontend Issues

1. **API Connection Failed**
   - Verify backend is running on http://localhost:8000
   - Check VITE_API_URL in .env
   - Check CORS settings in backend

2. **Build Errors**
   - Delete node_modules and package-lock.json
   - Run `npm install` again

3. **Page Not Found**
   - Check React Router configuration
   - Verify route paths match

## 📦 Production Deployment

### Backend

```bash
# Build Docker image
docker build -t smart-backend .

# Run with Docker Compose
docker-compose up -d
```

### Frontend

```bash
# Build for production
npm run build

# Deploy dist/ folder to:
# - Vercel
# - Netlify
# - AWS S3 + CloudFront
# - Any static hosting service
```

## 🎓 Learning Objectives

This project demonstrates:
- RESTful API design
- Database modeling and relationships
- Authentication and authorization
- State management in React
- TypeScript for type safety
- Modern web development practices
- Responsive design principles
- API integration

## 📄 License

Educational use only - Object-Oriented Programming Course Project

---

**Need help?** Check the documentation in each directory's README file.
