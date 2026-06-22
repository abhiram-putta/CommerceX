# Testing the sMart Backend API

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd /Users/shriyansp/Desktop/oopsProject
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements/base.txt
```

### 2. Setup Environment
```bash
# Copy environment file
cp .env.example .env

# Edit .env and set a SECRET_KEY
# You can generate one with: python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Start Database (Docker)
```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Or start all services
docker-compose up -d
```

### 4. Initialize Database
```bash
# Create initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migrations
alembic upgrade head
```

### 5. Run the Application
```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload

# Or using Python directly
python app/main.py
```

### 6. Access API Documentation
Open your browser and visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 📝 API Testing Guide

### Testing with Swagger UI (Easiest)

1. Go to http://localhost:8000/docs
2. Try the endpoints in order:

#### Step 1: Register a User
- Click on `POST /api/v1/auth/register`
- Click "Try it out"
- Modify the request body:
```json
{
  "email": "john@example.com",
  "password": "Test@1234",
  "phone": "+919876543210",
  "role": "customer",
  "full_name": "John Doe"
}
```
- Click "Execute"
- You should get a 201 response with user details

#### Step 2: Login
- Click on `POST /api/v1/auth/login`
- Click "Try it out"
- Enter:
  - email: `john@example.com`
  - password: `Test@1234`
- Click "Execute"
- Copy the `access_token` from the response

#### Step 3: Authorize (for protected endpoints)
- Click the "Authorize" button at the top right
- Paste your access token in the "Value" field
- Click "Authorize"
- Click "Close"

#### Step 4: Get Current User
- Click on `GET /api/v1/users/me`
- Click "Try it out"
- Click "Execute"
- You should see your user profile

#### Step 5: Update Profile
- Click on `PUT /api/v1/users/me/profile`
- Click "Try it out"
- Modify the request body:
```json
{
  "full_name": "John Doe",
  "city": "Mumbai",
  "state": "Maharashtra",
  "country": "India",
  "pincode": "400001",
  "preferences": {
    "favorite_categories": ["electronics", "books"]
  }
}
```
- Click "Execute"

---

### Testing with cURL

#### 1. Register User
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane@example.com",
    "password": "Secure@123",
    "phone": "+919876543211",
    "role": "retailer",
    "full_name": "Jane Smith"
  }'
```

#### 2. Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login?email=jane@example.com&password=Secure@123"
```

Save the access_token from response.

#### 3. Get Current User (with token)
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

#### 4. Update Profile
```bash
curl -X PUT "http://localhost:8000/api/v1/users/me/profile" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "Jane Electronics Store",
    "business_type": "Electronics Retail",
    "city": "Delhi",
    "state": "Delhi"
  }'
```

---

### Testing with Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# 1. Register
response = requests.post(f"{BASE_URL}/auth/register", json={
    "email": "test@example.com",
    "password": "Test@1234",
    "role": "customer",
    "full_name": "Test User"
})
print("Register:", response.json())

# 2. Login
response = requests.post(f"{BASE_URL}/auth/login", params={
    "email": "test@example.com",
    "password": "Test@1234"
})
tokens = response.json()
access_token = tokens["access_token"]
print("Login:", tokens)

# 3. Get current user
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.get(f"{BASE_URL}/users/me", headers=headers)
print("User:", response.json())

# 4. Update profile
response = requests.put(
    f"{BASE_URL}/users/me/profile",
    headers=headers,
    json={
        "full_name": "Test User Updated",
        "city": "Bangalore",
        "state": "Karnataka"
    }
)
print("Profile:", response.json())
```

---

## ✅ Available Endpoints

### Authentication (`/api/v1/auth`)
- ✅ `POST /register` - Register new user
- ✅ `POST /login` - Login and get JWT tokens
- ✅ `POST /refresh` - Refresh access token
- ✅ `POST /verify-email` - Verify email with token
- ✅ `POST /verify-phone` - Verify phone with OTP
- ✅ `POST /forgot-password` - Request password reset
- ✅ `POST /reset-password` - Reset password with token

### Users (`/api/v1/users`)
- ✅ `GET /me` - Get current user profile
- ✅ `PUT /me` - Update current user
- ✅ `DELETE /me` - Deactivate account
- ✅ `PUT /me/profile` - Update extended profile
- ✅ `GET /me/statistics` - Get user statistics

---

## 🔐 Authentication Flow

1. **Register** → Get user created
2. **Login** → Get `access_token` and `refresh_token`
3. **Use access_token** in subsequent requests:
   - Header: `Authorization: Bearer <access_token>`
4. **Refresh token** when access_token expires
5. **Logout** → Client should discard tokens

---

## 🧪 Test Scenarios

### Scenario 1: Customer Registration & Profile Setup
```
1. Register as customer
2. Login
3. Get profile (should show incomplete profile)
4. Update profile with address
5. Get profile again (should show updated data)
```

### Scenario 2: Retailer with Business Info
```
1. Register as retailer
2. Login
3. Update profile with business details
   - business_name
   - business_license
   - gst_number
4. Verify business info is saved
```

### Scenario 3: Authentication Errors
```
1. Try login with wrong password → 401 error
2. Try accessing /me without token → 401 error
3. Try accessing /me with invalid token → 401 error
4. Register with existing email → 409 error
```

### Scenario 4: Password Reset Flow
```
1. Request password reset → email sent (check logs)
2. Use reset token to reset password
3. Login with new password → success
4. Login with old password → fail
```

---

## 🐛 Common Issues

### Issue: "Connection refused" or "Cannot connect to database"
**Solution:**
```bash
# Make sure PostgreSQL is running
docker-compose up -d postgres

# Check if it's running
docker-compose ps

# Check logs
docker-compose logs postgres
```

### Issue: "SECRET_KEY not set"
**Solution:**
```bash
# Generate a secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Add to .env file
echo "SECRET_KEY=<generated_key>" >> .env
```

### Issue: "Table doesn't exist"
**Solution:**
```bash
# Run migrations
alembic upgrade head

# If migrations don't exist, create them
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

### Issue: "Module not found"
**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Install dependencies
pip install -r requirements/base.txt
```

---

## 📊 Expected Response Formats

### Success Response (Register/Login)
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "role": "customer",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  ...
}
```

### Token Response
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Error Response
```json
{
  "error": true,
  "message": "Email already registered",
  "details": {}
}
```

---

## 🎯 Next Steps

After testing auth endpoints, you can:
1. Implement product management endpoints
2. Test product CRUD operations
3. Implement cart functionality
4. Test order placement
5. And so on...

---

## 📝 Notes

- All timestamps are in UTC
- UUIDs are used for all IDs
- Passwords must meet strength requirements
- Tokens expire (access: 30 min, refresh: 7 days)
- Soft delete is used (is_active=False)

Happy Testing! 🚀
