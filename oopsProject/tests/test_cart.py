"""
Tests for cart endpoints.
"""
import pytest
from fastapi import status


@pytest.mark.unit
class TestCartEndpoints:
    """Test cart endpoints."""

    def test_get_empty_cart(self, client, auth_headers_customer):
        """Test getting empty cart."""
        response = client.get(
            "/api/v1/cart",
            headers=auth_headers_customer
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_add_to_cart(self, client, auth_headers_customer, test_product):
        """Test adding product to cart."""
        response = client.post(
            "/api/v1/cart",
            headers=auth_headers_customer,
            json={
                "product_id": str(test_product.id),
                "quantity": 2
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["product_id"] == str(test_product.id)
        assert data["quantity"] == 2

    def test_add_to_cart_invalid_quantity(self, client, auth_headers_customer, test_product):
        """Test adding invalid quantity to cart."""
        response = client.post(
            "/api/v1/cart",
            headers=auth_headers_customer,
            json={
                "product_id": str(test_product.id),
                "quantity": 0
            }
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_add_to_cart_exceeds_stock(self, client, auth_headers_customer, test_product):
        """Test adding quantity that exceeds stock."""
        response = client.post(
            "/api/v1/cart",
            headers=auth_headers_customer,
            json={
                "product_id": str(test_product.id),
                "quantity": 1000  # More than available stock
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_cart_item(self, client, auth_headers_customer, test_product):
        """Test updating cart item quantity."""
        # First add to cart
        add_response = client.post(
            "/api/v1/cart",
            headers=auth_headers_customer,
            json={
                "product_id": str(test_product.id),
                "quantity": 2
            }
        )
        assert add_response.status_code == status.HTTP_201_CREATED

        # Update quantity
        response = client.put(
            f"/api/v1/cart/{test_product.id}",
            headers=auth_headers_customer,
            json={"quantity": 5}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["quantity"] == 5

    def test_remove_from_cart(self, client, auth_headers_customer, test_product):
        """Test removing item from cart."""
        # First add to cart
        client.post(
            "/api/v1/cart",
            headers=auth_headers_customer,
            json={
                "product_id": str(test_product.id),
                "quantity": 2
            }
        )

        # Remove from cart
        response = client.delete(
            f"/api/v1/cart/{test_product.id}",
            headers=auth_headers_customer
        )
        assert response.status_code == status.HTTP_200_OK

        # Verify cart is empty
        get_response = client.get(
            "/api/v1/cart",
            headers=auth_headers_customer
        )
        assert len(get_response.json()) == 0

    def test_clear_cart(self, client, auth_headers_customer, test_product):
        """Test clearing entire cart."""
        # Add items to cart
        client.post(
            "/api/v1/cart",
            headers=auth_headers_customer,
            json={
                "product_id": str(test_product.id),
                "quantity": 2
            }
        )

        # Clear cart
        response = client.delete(
            "/api/v1/cart",
            headers=auth_headers_customer
        )
        assert response.status_code == status.HTTP_200_OK

        # Verify cart is empty
        get_response = client.get(
            "/api/v1/cart",
            headers=auth_headers_customer
        )
        assert len(get_response.json()) == 0

    def test_get_cart_count(self, client, auth_headers_customer, test_product):
        """Test getting cart item count."""
        # Add items to cart
        client.post(
            "/api/v1/cart",
            headers=auth_headers_customer,
            json={
                "product_id": str(test_product.id),
                "quantity": 3
            }
        )

        # Get count
        response = client.get(
            "/api/v1/cart/count",
            headers=auth_headers_customer
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 3

    def test_cart_requires_auth(self, client):
        """Test that cart endpoints require authentication."""
        response = client.get("/api/v1/cart")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
