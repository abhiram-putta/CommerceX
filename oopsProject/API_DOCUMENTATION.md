# sMart E-commerce API Documentation

Complete API documentation for the sMart e-commerce backend platform.

## Base URL

```
Development: http://localhost:8000
Production: https://api.smart.com
```

## API Version

Current Version: **v1**

All endpoints are prefixed with `/api/v1`

## Authentication

### Overview

The API uses JWT (JSON Web Token) authentication with access and refresh tokens.

### Authentication Flow

1. **Register** - Create a new account
2. **Login** - Get access and refresh tokens
3. **Use Access Token** - Include in `Authorization` header
4. **Refresh** - Get new tokens when access token expires

### Headers

```http
Authorization: Bearer <access_token>
Content-Type: application/json
```

### Token Expiration

- **Access Token**: 30 minutes
- **Refresh Token**: 7 days

## Rate Limiting

**Limit**: 60 requests per minute per user/IP

**Headers Returned**:
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1699564800
```

**Error Response** (429):
```json
{
  "error": true,
  "message": "Rate limit exceeded. Maximum 60 requests per 60 seconds."
}
```

## Response Format

### Success Response

```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... },
  "meta": {
    "pagination": {
      "total": 100,
      "page": 1,
      "page_size": 20,
      "total_pages": 5
    }
  }
}
```

### Error Response

```json
{
  "error": true,
  "message": "Error description",
  "details": {
    "field": "email",
    "reason": "Invalid format"
  }
}
```

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200  | OK - Request successful |
| 201  | Created - Resource created |
| 204  | No Content - Success, no data to return |
| 400  | Bad Request - Invalid request data |
| 401  | Unauthorized - Authentication required |
| 403  | Forbidden - Insufficient permissions |
| 404  | Not Found - Resource doesn't exist |
| 409  | Conflict - Resource conflict (duplicate) |
| 422  | Validation Error - Invalid data format |
| 429  | Too Many Requests - Rate limit exceeded |
| 500  | Internal Server Error - Server error |

## API Endpoints

### Authentication

#### Register User

```http
POST /api/v1/auth/register
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "role": "CUSTOMER"
}
```

**Response** (201):
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "role": "CUSTOMER",
  "created_at": "2024-01-01T12:00:00Z"
}
```

#### Login

```http
POST /api/v1/auth/login
```

**Request Body** (Form Data):
```
username: user@example.com
password: SecurePass123!
```

**Response** (200):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Get Current User

```http
GET /api/v1/auth/me
```

**Headers**: `Authorization: Bearer <token>`

**Response** (200):
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "role": "CUSTOMER"
}
```

#### Refresh Token

```http
POST /api/v1/auth/refresh
```

**Request Body**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Products

#### List Products

```http
GET /api/v1/products
```

**Query Parameters**:
- `page` (int): Page number (default: 1)
- `page_size` (int): Items per page (default: 20, max: 100)
- `category_id` (UUID): Filter by category
- `brand` (string): Filter by brand
- `is_local` (boolean): Filter local products
- `min_price` (float): Minimum price
- `max_price` (float): Maximum price
- `sort_by` (string): Sort field (price, rating, created_at)
- `order` (string): Sort order (asc, desc)

**Example**:
```http
GET /api/v1/products?page=1&page_size=20&category_id=<uuid>&min_price=100
```

**Response** (200):
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Product Name",
      "slug": "product-name",
      "base_price": 999.99,
      "discount_percentage": 10,
      "final_price": 899.99,
      "brand": "Brand Name",
      "average_rating": 4.5,
      "review_count": 120
    }
  ],
  "meta": {
    "pagination": {
      "total": 100,
      "page": 1,
      "page_size": 20,
      "total_pages": 5
    }
  }
}
```

#### Get Product Details

```http
GET /api/v1/products/{product_id}
```

**Response** (200):
```json
{
  "id": "uuid",
  "name": "iPhone 14 Pro",
  "description": "Latest iPhone with...",
  "base_price": 99999.00,
  "discount_percentage": 10,
  "brand": "Apple",
  "category_id": "uuid",
  "images": ["url1", "url2"],
  "specifications": {
    "color": "Space Black",
    "storage": "256GB"
  },
  "average_rating": 4.7,
  "review_count": 450,
  "stock_quantity": 50
}
```

#### Search Products

```http
GET /api/v1/products/search
```

**Query Parameters**:
- `q` (string, required): Search query
- `page` (int): Page number
- `page_size` (int): Items per page

**Example**:
```http
GET /api/v1/products/search?q=iphone&page=1
```

#### Create Product

```http
POST /api/v1/products
```

**Auth**: Required (Seller/Admin)

**Request Body**:
```json
{
  "name": "Product Name",
  "description": "Product description",
  "category_id": "uuid",
  "base_price": 999.99,
  "mrp": 1299.99,
  "brand": "Brand Name",
  "unit_type": "piece",
  "images": ["url1", "url2"],
  "specifications": {
    "key": "value"
  }
}
```

### Shopping Cart

#### Get Cart

```http
GET /api/v1/cart
```

**Auth**: Required

**Response** (200):
```json
[
  {
    "id": "uuid",
    "product_id": "uuid",
    "product": {
      "name": "Product Name",
      "base_price": 999.99
    },
    "quantity": 2,
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

#### Add to Cart

```http
POST /api/v1/cart
```

**Auth**: Required

**Request Body**:
```json
{
  "product_id": "uuid",
  "quantity": 2
}
```

#### Update Cart Item

```http
PUT /api/v1/cart/{product_id}
```

**Auth**: Required

**Request Body**:
```json
{
  "quantity": 5
}
```

#### Remove from Cart

```http
DELETE /api/v1/cart/{product_id}
```

**Auth**: Required

#### Clear Cart

```http
DELETE /api/v1/cart
```

**Auth**: Required

### Orders

#### Create Order

```http
POST /api/v1/orders
```

**Auth**: Required

**Request Body**:
```json
{
  "shipping_address": {
    "street": "123 Main St",
    "city": "Mumbai",
    "state": "Maharashtra",
    "postal_code": "400001",
    "country": "India"
  },
  "payment_method": "RAZORPAY"
}
```

**Response** (201):
```json
{
  "id": "uuid",
  "order_number": "ORD-2024-00001",
  "status": "PENDING",
  "total_amount": 2499.98,
  "items": [...],
  "shipping_address": {...},
  "created_at": "2024-01-01T12:00:00Z"
}
```

#### List User Orders

```http
GET /api/v1/orders
```

**Auth**: Required

**Query Parameters**:
- `page` (int): Page number
- `page_size` (int): Items per page
- `status` (string): Filter by status

#### Get Order Details

```http
GET /api/v1/orders/{order_id}
```

**Auth**: Required

#### Cancel Order

```http
POST /api/v1/orders/{order_id}/cancel
```

**Auth**: Required

**Request Body**:
```json
{
  "reason": "Changed my mind"
}
```

#### Track Order

```http
GET /api/v1/orders/{order_id}/track
```

**Auth**: Required

**Response** (200):
```json
{
  "order_id": "uuid",
  "status": "SHIPPED",
  "timeline": [
    {
      "status": "PENDING",
      "timestamp": "2024-01-01T12:00:00Z"
    },
    {
      "status": "CONFIRMED",
      "timestamp": "2024-01-01T13:00:00Z"
    }
  ]
}
```

### Payments

#### Initiate Payment

```http
POST /api/v1/payments/initiate
```

**Auth**: Required

**Request Body**:
```json
{
  "order_id": "uuid"
}
```

**Response** (200):
```json
{
  "razorpay_order_id": "order_xyz123",
  "amount": 249998,
  "currency": "INR",
  "key_id": "rzp_test_..."
}
```

#### Verify Payment

```http
POST /api/v1/payments/verify
```

**Auth**: Required

**Request Body**:
```json
{
  "order_id": "uuid",
  "razorpay_payment_id": "pay_xyz123",
  "razorpay_order_id": "order_xyz123",
  "razorpay_signature": "signature"
}
```

### Reviews

#### Create Review

```http
POST /api/v1/reviews
```

**Auth**: Required

**Request Body**:
```json
{
  "product_id": "uuid",
  "rating": 5,
  "title": "Great product!",
  "comment": "Loved it, highly recommend"
}
```

#### Get Product Reviews

```http
GET /api/v1/reviews/product/{product_id}
```

**Query Parameters**:
- `page` (int): Page number
- `rating` (int): Filter by rating (1-5)

### WebSocket Endpoints

#### Real-time Notifications

```
ws://localhost:8000/ws/notifications?token=<jwt_token>
```

**Message Format**:
```json
{
  "type": "notification",
  "data": {
    "title": "Order Shipped",
    "message": "Your order has been shipped",
    "notification_type": "ORDER_UPDATE"
  }
}
```

#### Order Tracking

```
ws://localhost:8000/ws/orders/{order_id}?token=<jwt_token>
```

## Error Codes

| Code | Description |
|------|-------------|
| AUTH_FAILED | Authentication failed |
| INVALID_TOKEN | Token is invalid or expired |
| PERMISSION_DENIED | Insufficient permissions |
| RESOURCE_NOT_FOUND | Resource doesn't exist |
| VALIDATION_ERROR | Data validation failed |
| DUPLICATE_RESOURCE | Resource already exists |
| INSUFFICIENT_STOCK | Not enough stock available |
| PAYMENT_FAILED | Payment processing failed |
| RATE_LIMIT_EXCEEDED | Too many requests |

## SDKs and Code Examples

### Python

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    data={"username": "user@example.com", "password": "password"}
)
token = response.json()["access_token"]

# Get products
headers = {"Authorization": f"Bearer {token}"}
products = requests.get(
    "http://localhost:8000/api/v1/products",
    headers=headers
).json()
```

### JavaScript

```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: 'username=user@example.com&password=password'
});
const { access_token } = await loginResponse.json();

// Get products
const productsResponse = await fetch('http://localhost:8000/api/v1/products', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
const products = await productsResponse.json();
```

### cURL

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -d "username=user@example.com&password=password"

# Get products
curl -X GET http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer <token>"
```

## Best Practices

1. **Always use HTTPS in production**
2. **Store tokens securely** (HttpOnly cookies or secure storage)
3. **Implement token refresh** before expiration
4. **Handle rate limits** with exponential backoff
5. **Validate input** on client side
6. **Use pagination** for list endpoints
7. **Cache responses** where appropriate
8. **Handle errors gracefully**

## Support

- **Documentation**: https://docs.smart.com
- **API Status**: https://status.smart.com
- **Email**: api-support@smart.com
- **GitHub Issues**: https://github.com/smart/backend/issues
