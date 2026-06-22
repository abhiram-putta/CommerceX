"""
Tests for product endpoints.
"""
import pytest
from fastapi import status
from uuid import uuid4


@pytest.mark.unit
class TestProductEndpoints:
    """Test product endpoints."""

    def test_list_products(self, client, test_product):
        """Test listing products."""
        response = client.get("/api/v1/products")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_product(self, client, test_product):
        """Test getting single product."""
        response = client.get(f"/api/v1/products/{test_product.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(test_product.id)
        assert data["name"] == test_product.name

    def test_get_product_not_found(self, client):
        """Test getting non-existent product."""
        fake_id = uuid4()
        response = client.get(f"/api/v1/products/{fake_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_product_as_seller(self, client, auth_headers_seller, test_category):
        """Test creating product as seller."""
        response = client.post(
            "/api/v1/products",
            headers=auth_headers_seller,
            json={
                "name": "New Product",
                "description": "A brand new product",
                "short_description": "New product",
                "category_id": str(test_category.id),
                "base_price": 499.99,
                "mrp": 599.99,
                "unit_type": "piece",
                "unit_value": 1.0,
                "brand": "TestBrand"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "New Product"
        assert data["base_price"] == 499.99

    def test_create_product_as_customer_forbidden(self, client, auth_headers_customer, test_category):
        """Test creating product as customer (should fail)."""
        response = client.post(
            "/api/v1/products",
            headers=auth_headers_customer,
            json={
                "name": "New Product",
                "description": "A brand new product",
                "category_id": str(test_category.id),
                "base_price": 499.99,
                "unit_type": "piece"
            }
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_product(self, client, auth_headers_seller, test_product):
        """Test updating product."""
        response = client.put(
            f"/api/v1/products/{test_product.id}",
            headers=auth_headers_seller,
            json={
                "name": "Updated Product Name",
                "base_price": 1099.99
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Product Name"
        assert data["base_price"] == 1099.99

    def test_delete_product(self, client, auth_headers_seller, test_product):
        """Test deleting product."""
        response = client.delete(
            f"/api/v1/products/{test_product.id}",
            headers=auth_headers_seller
        )
        assert response.status_code == status.HTTP_200_OK

        # Verify product is deleted
        get_response = client.get(f"/api/v1/products/{test_product.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_search_products(self, client, test_product):
        """Test searching products."""
        response = client.get(
            "/api/v1/products/search",
            params={"q": "Test"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_filter_products_by_category(self, client, test_product, test_category):
        """Test filtering products by category."""
        response = client.get(
            "/api/v1/products",
            params={"category_id": str(test_category.id)}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert data[0]["category_id"] == str(test_category.id)

    def test_filter_products_by_price_range(self, client, test_product):
        """Test filtering products by price range."""
        response = client.get(
            "/api/v1/products",
            params={
                "min_price": 500,
                "max_price": 1500
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        for product in data:
            assert 500 <= product["base_price"] <= 1500
