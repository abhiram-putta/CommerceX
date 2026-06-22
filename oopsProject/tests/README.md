# Test Suite

This directory contains the test suite for the sMart e-commerce backend.

## Setup

1. Install test dependencies:
```bash
pip install -r requirements/dev.txt
```

2. Make sure your test database is configured in `.env`

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_auth.py
```

### Run specific test
```bash
pytest tests/test_auth.py::TestAuthEndpoints::test_login_success
```

### Run tests by marker
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

### Run in verbose mode
```bash
pytest -v
```

## Test Structure

- `conftest.py` - Shared fixtures and test configuration
- `test_auth.py` - Authentication endpoint tests
- `test_products.py` - Product CRUD and search tests
- `test_cart.py` - Shopping cart functionality tests
- `test_orders.py` - Order creation and management tests
- `test_payments.py` - Payment processing tests

## Test Fixtures

### User Fixtures
- `test_customer` - Customer user account
- `test_seller` - Seller user account
- `test_admin` - Admin user account
- `customer_token` - JWT token for customer
- `seller_token` - JWT token for seller
- `admin_token` - JWT token for admin
- `auth_headers_customer` - Auth headers for customer
- `auth_headers_seller` - Auth headers for seller
- `auth_headers_admin` - Auth headers for admin

### Data Fixtures
- `test_category` - Sample category
- `test_product` - Sample product
- `cart_with_items` - Cart with test items

### Database Fixtures
- `db_session` - Database session for tests
- `client` - Test client for API requests
- `async_client` - Async test client

## Coverage

The test suite aims for 80% code coverage. View the coverage report:

```bash
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## Writing Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Test Markers
Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_simple_function():
    pass

@pytest.mark.integration
def test_api_endpoint():
    pass

@pytest.mark.slow
def test_long_running_task():
    pass
```

### Example Test
```python
import pytest
from fastapi import status

@pytest.mark.unit
def test_example(client, auth_headers_customer):
    response = client.get(
        "/api/v1/endpoint",
        headers=auth_headers_customer
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["key"] == "expected_value"
```

## Continuous Integration

Tests are automatically run on:
- Every commit to main branch
- Every pull request
- Scheduled nightly builds

## Troubleshooting

### Database Connection Issues
Make sure SQLite is available for in-memory test database.

### Import Errors
Ensure all dependencies are installed:
```bash
pip install -r requirements/dev.txt
```

### Async Test Warnings
The test suite uses `pytest-asyncio` with `asyncio_mode = auto` in `pytest.ini`.
