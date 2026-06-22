"""
Tests for order endpoints.
"""
import pytest
from fastapi import status


@pytest.mark.integration
class TestOrderEndpoints:
    """Test order endpoints."""

    @pytest.fixture
    async def cart_with_items(self, client, auth_headers_customer, test_product):
        """Add items to cart before tests."""
        client.post(
            "/api/v1/cart",
            headers=auth_headers_customer,
            json={
                "product_id": str(test_product.id),
                "quantity": 2
            }
        )
        yield
        # Cleanup
        client.delete("/api/v1/cart", headers=auth_headers_customer)

    def test_create_order_from_cart(self, client, auth_headers_customer, cart_with_items):
        """Test creating order from cart."""
        response = client.post(
            "/api/v1/orders",
            headers=auth_headers_customer,
            json={
                "shipping_address": {
                    "street": "123 Test St",
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "postal_code": "400001",
                    "country": "India"
                },
                "payment_method": "COD"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "order_number" in data
        assert data["status"] == "PENDING"
        assert len(data["items"]) > 0

    def test_create_order_empty_cart(self, client, auth_headers_customer):
        """Test creating order with empty cart."""
        response = client.post(
            "/api/v1/orders",
            headers=auth_headers_customer,
            json={
                "shipping_address": {
                    "street": "123 Test St",
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "postal_code": "400001",
                    "country": "India"
                },
                "payment_method": "COD"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_user_orders(self, client, auth_headers_customer, cart_with_items):
        """Test listing user orders."""
        # Create an order first
        client.post(
            "/api/v1/orders",
            headers=auth_headers_customer,
            json={
                "shipping_address": {
                    "street": "123 Test St",
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "postal_code": "400001",
                    "country": "India"
                },
                "payment_method": "COD"
            }
        )

        # List orders
        response = client.get(
            "/api/v1/orders",
            headers=auth_headers_customer
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_order_details(self, client, auth_headers_customer, cart_with_items):
        """Test getting order details."""
        # Create an order
        create_response = client.post(
            "/api/v1/orders",
            headers=auth_headers_customer,
            json={
                "shipping_address": {
                    "street": "123 Test St",
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "postal_code": "400001",
                    "country": "India"
                },
                "payment_method": "COD"
            }
        )
        order_id = create_response.json()["id"]

        # Get order details
        response = client.get(
            f"/api/v1/orders/{order_id}",
            headers=auth_headers_customer
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == order_id

    def test_cancel_order(self, client, auth_headers_customer, cart_with_items):
        """Test canceling order."""
        # Create an order
        create_response = client.post(
            "/api/v1/orders",
            headers=auth_headers_customer,
            json={
                "shipping_address": {
                    "street": "123 Test St",
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "postal_code": "400001",
                    "country": "India"
                },
                "payment_method": "COD"
            }
        )
        order_id = create_response.json()["id"]

        # Cancel order
        response = client.post(
            f"/api/v1/orders/{order_id}/cancel",
            headers=auth_headers_customer,
            json={"reason": "Changed my mind"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "CANCELLED"

    def test_track_order(self, client, auth_headers_customer, cart_with_items):
        """Test tracking order."""
        # Create an order
        create_response = client.post(
            "/api/v1/orders",
            headers=auth_headers_customer,
            json={
                "shipping_address": {
                    "street": "123 Test St",
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "postal_code": "400001",
                    "country": "India"
                },
                "payment_method": "COD"
            }
        )
        order_id = create_response.json()["id"]

        # Track order
        response = client.get(
            f"/api/v1/orders/{order_id}/track",
            headers=auth_headers_customer
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "status" in data
        assert "timeline" in data

    def test_orders_require_auth(self, client):
        """Test that order endpoints require authentication."""
        response = client.get("/api/v1/orders")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_cannot_access_other_user_order(self, client, auth_headers_customer, auth_headers_seller, cart_with_items):
        """Test that users cannot access other users' orders."""
        # Create order as customer
        create_response = client.post(
            "/api/v1/orders",
            headers=auth_headers_customer,
            json={
                "shipping_address": {
                    "street": "123 Test St",
                    "city": "Mumbai",
                    "state": "Maharashtra",
                    "postal_code": "400001",
                    "country": "India"
                },
                "payment_method": "COD"
            }
        )
        order_id = create_response.json()["id"]

        # Try to access as seller
        response = client.get(
            f"/api/v1/orders/{order_id}",
            headers=auth_headers_seller
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
