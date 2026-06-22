"""
Pytest configuration and shared fixtures.
"""
import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.config.database import Base, get_db
from app.config.settings import Settings, get_settings
from app.main import app
from app.models.user import User, UserRole
from app.models.category import Category
from app.models.product import Product
from app.utils.security import hash_password


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    """Create test database engine."""
    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=False
    )

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield test_engine

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


@pytest.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Create database session for tests."""
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """Override database dependency."""
    async def _override_get_db():
        yield db_session

    return _override_get_db


@pytest.fixture
def test_settings() -> Settings:
    """Get test settings."""
    settings = get_settings()
    settings.TESTING = True
    return settings


@pytest.fixture
def client(override_get_db) -> TestClient:
    """Create test client."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# User fixtures
@pytest.fixture
async def test_customer(db_session: AsyncSession) -> User:
    """Create test customer user."""
    user = User(
        id=uuid4(),
        email="customer@test.com",
        username="testcustomer",
        full_name="Test Customer",
        password_hash=hash_password("testpass123"),
        role=UserRole.CUSTOMER,
        email_verified=True,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_seller(db_session: AsyncSession) -> User:
    """Create test seller user."""
    user = User(
        id=uuid4(),
        email="seller@test.com",
        username="testseller",
        full_name="Test Seller",
        password_hash=hash_password("testpass123"),
        role=UserRole.SELLER,
        email_verified=True,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_admin(db_session: AsyncSession) -> User:
    """Create test admin user."""
    user = User(
        id=uuid4(),
        email="admin@test.com",
        username="testadmin",
        full_name="Test Admin",
        password_hash=hash_password("testpass123"),
        role=UserRole.ADMIN,
        email_verified=True,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


# Category fixtures
@pytest.fixture
async def test_category(db_session: AsyncSession) -> Category:
    """Create test category."""
    category = Category(
        id=uuid4(),
        name="Electronics",
        slug="electronics",
        description="Electronic products",
        is_active=True
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


# Product fixtures
@pytest.fixture
async def test_product(db_session: AsyncSession, test_category: Category, test_seller: User) -> Product:
    """Create test product."""
    product = Product(
        id=uuid4(),
        name="Test Product",
        slug="test-product",
        description="A test product for testing",
        short_description="Test product",
        category_id=test_category.id,
        seller_id=test_seller.id,
        base_price=999.99,
        mrp=1299.99,
        discount_percentage=10.0,
        brand="TestBrand",
        unit_type="piece",
        unit_value=1.0,
        is_active=True,
        stock_quantity=100
    )
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)
    return product


# Auth token fixtures
@pytest.fixture
def customer_token(client, test_customer: User) -> str:
    """Get auth token for customer."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "customer@test.com",
            "password": "testpass123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def seller_token(client, test_seller: User) -> str:
    """Get auth token for seller."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "seller@test.com",
            "password": "testpass123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def admin_token(client, test_admin: User) -> str:
    """Get auth token for admin."""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin@test.com",
            "password": "testpass123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def auth_headers_customer(customer_token: str) -> dict:
    """Get auth headers for customer."""
    return {"Authorization": f"Bearer {customer_token}"}


@pytest.fixture
def auth_headers_seller(seller_token: str) -> dict:
    """Get auth headers for seller."""
    return {"Authorization": f"Bearer {seller_token}"}


@pytest.fixture
def auth_headers_admin(admin_token: str) -> dict:
    """Get auth headers for admin."""
    return {"Authorization": f"Bearer {admin_token}"}
