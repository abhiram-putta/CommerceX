# sMart API Quick Reference

## 🔐 Authentication Endpoints

### Register New User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123",
  "full_name": "John Doe",
  "phone": "+919876543210",
  "role": "customer"
}
```

### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "securePassword123"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJh...",
  "token_type": "bearer"
}
```

---

## 👤 User Endpoints

### Get Current User Profile
```http
GET /api/v1/users/me
Authorization: Bearer YOUR_TOKEN
```

### Update Profile
```http
PUT /api/v1/users/me
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "full_name": "Jane Doe",
  "phone": "+919876543210"
}
```

---

## 📦 Product Endpoints

### List Products (Paginated)
```http
GET /api/v1/products?page=1&page_size=20
GET /api/v1/products?category_id={uuid}&brand=Apple&is_local=true
```

### Search Products (with ML Semantic Search)
```http
GET /api/v1/products/search?q=smartphone%20with%20good%20camera&limit=20
GET /api/v1/products/search?q=laptop&category_id={uuid}&min_price=50000&max_price=100000
```

### Get Product Details
```http
GET /api/v1/products/{product_id}
```

### Get Featured Products
```http
GET /api/v1/products/featured?limit=10
```

### Create Product (Sellers Only)
```http
POST /api/v1/products
Authorization: Bearer SELLER_TOKEN
Content-Type: application/json

{
  "name": "iPhone 15 Pro",
  "short_description": "Latest iPhone with A17 Pro chip",
  "description": "Full description here...",
  "price": 134900.0,
  "category_id": "{uuid}",
  "brand": "Apple",
  "sku": "IPH15PRO",
  "stock_quantity": 100,
  "is_local_product": false
}
```

### Update Product (Sellers Only)
```http
PUT /api/v1/products/{product_id}
Authorization: Bearer SELLER_TOKEN
Content-Type: application/json

{
  "price": 129900.0,
  "stock_quantity": 150
}
```

### Delete Product (Sellers Only)
```http
DELETE /api/v1/products/{product_id}
Authorization: Bearer SELLER_TOKEN
```

---

## 🏷️ Category Endpoints

### List Categories
```http
GET /api/v1/categories
GET /api/v1/categories?parent_id={uuid}  # Get subcategories
```

### Get Category Details
```http
GET /api/v1/categories/{category_id}
```

### Create Category (Admin Only)
```http
POST /api/v1/categories
Authorization: Bearer ADMIN_TOKEN
Content-Type: application/json

{
  "name": "Smartphones",
  "slug": "smartphones",
  "description": "Latest smartphones",
  "parent_id": "{uuid}",  # Optional
  "is_active": true,
  "is_featured": true
}
```

---

## 🤖 ML Recommendation Endpoints (NEW!)

### Get Personalized Recommendations
```http
GET /api/v1/recommendations/for-you?top_n=10
Authorization: Bearer YOUR_TOKEN

Response:
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "recommendations": [
    {
      "product_id": "456e7890-...",
      "score": 0.92,
      "product": {
        "id": "456e7890-...",
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

### Get Similar Products
```http
GET /api/v1/recommendations/similar/{product_id}?top_n=5

Response:
{
  "product_id": "456e7890-...",
  "similar_products": [
    {
      "product_id": "789e0123-...",
      "score": 0.88,
      "product": { ... }
    }
  ],
  "total": 5
}
```

### Get Trending Products
```http
GET /api/v1/recommendations/trending?top_n=10
GET /api/v1/recommendations/trending?top_n=10&category_id={uuid}
```

---

## 📊 Response Formats

### Success Response (Single Object)
```json
{
  "id": "123e4567-...",
  "name": "Product Name",
  "price": 1299.0,
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:00:00"
}
```

### Success Response (Paginated)
```json
{
  "items": [ ... ],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "pages": 8
}
```

### Error Response
```json
{
  "detail": "Error message here"
}
```

---

## 🔑 Authentication Headers

Include in all authenticated requests:
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

---

## 📝 Query Parameters

### Pagination
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

### Filters
- `category_id`: Filter by category UUID
- `brand`: Filter by brand name
- `is_local`: Filter local products (true/false)
- `min_price`: Minimum price
- `max_price`: Maximum price

### Search
- `q`: Search query string
- `limit`: Max results (default: 20, max: 100)

### Recommendations
- `top_n`: Number of recommendations (default: 10, max: 50)

---

## 🚦 HTTP Status Codes

- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Missing/invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

---

## 💡 Common Use Cases

### Homepage Flow
```http
# 1. Get featured products
GET /api/v1/products/featured?limit=6

# 2. Get trending products
GET /api/v1/recommendations/trending?top_n=10

# 3. Get personalized recommendations (if logged in)
GET /api/v1/recommendations/for-you?top_n=6
Authorization: Bearer TOKEN
```

### Product Detail Page Flow
```http
# 1. Get product details
GET /api/v1/products/{product_id}

# 2. Get similar products
GET /api/v1/recommendations/similar/{product_id}?top_n=4
```

### Search Flow
```http
# 1. Search products with ML
GET /api/v1/products/search?q=laptop%20for%20gaming

# 2. Refine search with filters
GET /api/v1/products/search?q=laptop&min_price=50000&max_price=150000&brand=Dell
```

### Category Browse Flow
```http
# 1. Get all categories
GET /api/v1/categories

# 2. Get products in category
GET /api/v1/products?category_id={uuid}&page=1&page_size=20

# 3. Get subcategories
GET /api/v1/categories?parent_id={uuid}
```

---

## 🔧 Testing with cURL

### Register & Login
```bash
# Register
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#",
    "full_name": "Test User",
    "phone": "+919876543210",
    "role": "customer"
  }'

# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test@example.com",
    "password": "Test123!@#"
  }'
```

### Search Products
```bash
curl -X GET "http://localhost:8000/api/v1/products/search?q=smartphone&limit=10"
```

### Get Recommendations
```bash
curl -X GET "http://localhost:8000/api/v1/recommendations/for-you?top_n=10" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## 🌐 Base URL

**Development**: `http://localhost:8000`
**API Version**: `v1`
**Full Base**: `http://localhost:8000/api/v1`

---

## 📖 Interactive Documentation

Visit these URLs when server is running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🎯 Quick Tips

1. **Always include Authorization header** for protected endpoints
2. **Use semantic search** for better product discovery
3. **Paginate large result sets** to improve performance
4. **Cache recommendations** on frontend (TTL: 5-10 minutes)
5. **Handle 401 errors** by refreshing tokens or re-authenticating
6. **Validate UUIDs** before making requests

---

## 📦 Response Examples

### Product List Response
```json
{
  "items": [
    {
      "id": "123e4567-...",
      "name": "iPhone 14 Pro",
      "slug": "iphone-14-pro",
      "short_description": "Latest iPhone",
      "price": 129900.0,
      "compare_at_price": 134900.0,
      "brand": "Apple",
      "image_url": "https://...",
      "is_featured": true,
      "is_local_product": false,
      "category": {
        "id": "456e7890-...",
        "name": "Smartphones",
        "slug": "smartphones"
      },
      "average_rating": 4.5,
      "review_count": 128,
      "created_at": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 20,
  "pages": 8
}
```

### Recommendation Response
```json
{
  "user_id": "123e4567-...",
  "recommendations": [
    {
      "product_id": "456e7890-...",
      "score": 0.92,
      "product": {
        "id": "456e7890-...",
        "name": "Samsung Galaxy S23",
        "price": 89900.0,
        "brand": "Samsung",
        "image_url": "https://...",
        "average_rating": 4.3
      }
    }
  ],
  "total": 10,
  "algorithm": "collaborative_filtering"
}
```

---

Happy coding! 🚀
