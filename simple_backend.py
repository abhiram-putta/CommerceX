"""
Simple FastAPI backend with mock data for testing frontend
"""
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta
import os
import uuid
import jwt
import bcrypt

app = FastAPI(title="sMart Backend API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock database
users_db = {}
products_db = []
categories_db = []
cart_db = {}
orders_db = {}
SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable must be set")

# Pydantic models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: Optional[str] = "customer"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class User(BaseModel):
    id: str
    email: str
    role: str
    is_active: bool = True
    is_verified: bool = True
    email_verified: bool = True
    phone_verified: bool = False
    profile_completion: int = 75
    created_at: str
    updated_at: str
    profile: Optional[dict] = None

# Initialize sample data
def init_sample_data():
    global products_db, categories_db

    # Sample categories
    categories_db = [
        {"id": str(uuid.uuid4()), "name": "Electronics", "description": "Electronic devices and gadgets", "is_active": True, "display_order": 1},
        {"id": str(uuid.uuid4()), "name": "Clothing", "description": "Fashion and apparel", "is_active": True, "display_order": 2},
        {"id": str(uuid.uuid4()), "name": "Home & Kitchen", "description": "Home essentials", "is_active": True, "display_order": 3},
        {"id": str(uuid.uuid4()), "name": "Books", "description": "Books and magazines", "is_active": True, "display_order": 4},
        {"id": str(uuid.uuid4()), "name": "Sports", "description": "Sports equipment", "is_active": True, "display_order": 5},
    ]

    # Sample products
    products = [
        {
            "name": "Wireless Headphones",
            "description": "Premium noise-cancelling wireless headphones with 30-hour battery life",
            "brand": "AudioPro",
            "base_price": 149.99,
            "category": 0,
            "images": ["https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800"],
            "tags": ["electronics", "audio", "wireless"]
        },
        {
            "name": "Smart Watch Series X",
            "description": "Latest smartwatch with health tracking and GPS",
            "brand": "TechWear",
            "base_price": 399.99,
            "category": 0,
            "images": ["https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800"],
            "tags": ["electronics", "smartwatch", "fitness"]
        },
        {
            "name": "Leather Jacket",
            "description": "Genuine leather jacket, perfect for all seasons",
            "brand": "StyleCo",
            "base_price": 199.99,
            "category": 1,
            "images": ["https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800"],
            "tags": ["clothing", "leather", "jacket"]
        },
        {
            "name": "Running Shoes",
            "description": "Professional running shoes with advanced cushioning",
            "brand": "SportMax",
            "base_price": 89.99,
            "category": 4,
            "images": ["https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800"],
            "tags": ["sports", "shoes", "running"]
        },
        {
            "name": "Coffee Maker Pro",
            "description": "Programmable coffee maker with thermal carafe",
            "brand": "BrewMaster",
            "base_price": 129.99,
            "category": 2,
            "images": ["https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=800"],
            "tags": ["kitchen", "coffee", "appliance"]
        },
        {
            "name": "Bestseller Novel",
            "description": "Captivating fiction novel by award-winning author",
            "brand": "Classic Books",
            "base_price": 24.99,
            "category": 3,
            "images": ["https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=800"],
            "tags": ["books", "fiction", "bestseller"]
        },
    ]

    for i, p in enumerate(products):
        product = {
            "id": str(uuid.uuid4()),
            "name": p["name"],
            "description": p["description"],
            "brand": p["brand"],
            "category_id": categories_db[p["category"]]["id"],
            "category": categories_db[p["category"]],
            "base_price": p["base_price"],
            "is_local_product": i % 2 == 0,
            "is_featured": i < 3,
            "is_active": True,
            "images": p["images"],
            "specifications": {},
            "tags": p["tags"],
            "avg_rating": 4.0 + (i % 10) / 10,
            "review_count": 10 + i * 5,
            "view_count": 100 + i * 50,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        products_db.append(product)

init_sample_data()

# Helper functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

# Routes
@app.get("/")
async def root():
    return {"message": "sMart API Server", "status": "running"}

@app.post("/api/v1/auth/register")
async def register(user_data: UserRegister):
    if user_data.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = str(uuid.uuid4())
    hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    user = {
        "id": user_id,
        "email": user_data.email,
        "password": hashed_password,
        "role": user_data.role,
        "is_active": True,
        "is_verified": True,
        "email_verified": True,
        "phone_verified": False,
        "profile_completion": 75,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "profile": {
            "full_name": user_data.full_name,
            "country": "US",
            "preferences": {}
        }
    }

    users_db[user_data.email] = user

    return {
        "id": user_id,
        "email": user_data.email,
        "role": user_data.role,
        "is_active": True,
        "is_verified": True,
        "email_verified": True,
        "phone_verified": False,
        "profile_completion": 75,
        "created_at": user["created_at"],
        "updated_at": user["updated_at"],
        "profile": user["profile"]
    }

@app.post("/api/v1/auth/login")
async def login(credentials: UserLogin):
    user = users_db.get(credentials.email)
    if not user or not bcrypt.checkpw(credentials.password.encode('utf-8'), user["password"].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": user["email"], "user_id": user["id"]})
    refresh_token = create_refresh_token({"sub": user["email"], "user_id": user["id"]})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.get("/api/v1/auth/me")
async def get_current_user():
    # Return mock user for testing
    return {
        "id": str(uuid.uuid4()),
        "email": "test@example.com",
        "role": "customer",
        "is_active": True,
        "is_verified": True,
        "email_verified": True,
        "phone_verified": False,
        "profile_completion": 75,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "profile": {"full_name": "Test User", "country": "US", "preferences": {}}
    }

@app.get("/api/v1/products")
async def get_products(
    page: int = 1,
    page_size: int = 12,
    search: Optional[str] = None,
    category_id: Optional[str] = None
):
    filtered_products = products_db

    if search:
        filtered_products = [p for p in filtered_products if search.lower() in p["name"].lower() or search.lower() in p["description"].lower()]

    if category_id:
        filtered_products = [p for p in filtered_products if p["category_id"] == category_id]

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    return {
        "items": filtered_products[start_idx:end_idx],
        "total": len(filtered_products),
        "page": page,
        "page_size": page_size,
        "pages": (len(filtered_products) + page_size - 1) // page_size
    }

@app.get("/api/v1/products/featured")
async def get_featured_products():
    return [p for p in products_db if p["is_featured"]][:6]

@app.get("/api/v1/products/{product_id}")
async def get_product(product_id: str):
    product = next((p for p in products_db if p["id"] == product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.get("/api/v1/categories")
async def get_categories():
    return categories_db

@app.get("/api/v1/recommendations/trending")
async def get_trending_products(top_n: int = 10, category_id: Optional[str] = None):
    """Get trending products based on view count"""
    trending = sorted(products_db, key=lambda p: p["view_count"], reverse=True)
    if category_id:
        trending = [p for p in trending if p["category_id"] == category_id]
    return trending[:top_n]

@app.get("/api/v1/cart")
async def get_cart():
    return {
        "items": [],
        "subtotal": 0.0,
        "tax": 0.0,
        "delivery_charge": 0.0,
        "total": 0.0,
        "item_count": 0
    }

@app.get("/api/v1/wishlist")
async def get_wishlist():
    return []

@app.get("/api/v1/orders")
async def get_orders():
    return {
        "items": [],
        "total": 0,
        "page": 1,
        "page_size": 10,
        "pages": 0
    }

@app.get("/api/v1/notifications")
async def get_notifications():
    return {
        "items": [],
        "total": 0,
        "page": 1,
        "page_size": 20,
        "pages": 0
    }

@app.get("/api/v1/notifications/unread-count")
async def get_unread_count():
    return {"count": 0}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
