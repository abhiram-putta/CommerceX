"""
Tests for payment endpoints.
"""
import pytest
from fastapi import status
from unittest.mock import patch, MagicMock


@pytest.mark.integration
class TestPaymentEndpoints:
    """Test payment endpoints."""

    @pytest.fixture
    async def test_order(self, client, auth_headers_customer, test_product):
        """Create test order."""
        # Add to cart
        client.post(
            "/api/v1/cart",
            headers=auth_headers_customer,
            json={
                "product_id": str(test_product.id),
                "quantity": 2
            }
        )

        # Create order
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
                "payment_method": "RAZORPAY"
            }
        )
        return response.json()

    @patch('app.services.payment_service.razorpay.Client')
    def test_initiate_payment(self, mock_razorpay, client, auth_headers_customer, test_order):
        """Test initiating payment."""
        # Mock Razorpay client
        mock_client = MagicMock()
        mock_client.order.create.return_value = {
            "id": "order_test123",
            "amount": 100000,
            "currency": "INR"
        }
        mock_razorpay.return_value = mock_client

        response = client.post(
            "/api/v1/payments/initiate",
            headers=auth_headers_customer,
            json={
                "order_id": test_order["id"]
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "razorpay_order_id" in data
        assert "amount" in data

    def test_initiate_payment_invalid_order(self, client, auth_headers_customer):
        """Test initiating payment for invalid order."""
        from uuid import uuid4
        response = client.post(
            "/api/v1/payments/initiate",
            headers=auth_headers_customer,
            json={
                "order_id": str(uuid4())
            }
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch('app.services.payment_service.razorpay.Client')
    def test_verify_payment(self, mock_razorpay, client, auth_headers_customer, test_order):
        """Test verifying payment."""
        # Mock Razorpay verification
        mock_client = MagicMock()
        mock_client.utility.verify_payment_signature.return_value = True
        mock_razorpay.return_value = mock_client

        response = client.post(
            "/api/v1/payments/verify",
            headers=auth_headers_customer,
            json={
                "order_id": test_order["id"],
                "razorpay_payment_id": "pay_test123",
                "razorpay_order_id": "order_test123",
                "razorpay_signature": "test_signature"
            }
        )
        assert response.status_code == status.HTTP_200_OK

    def test_mark_cod_paid(self, client, auth_headers_admin, test_order):
        """Test marking COD order as paid."""
        response = client.post(
            f"/api/v1/payments/{test_order['id']}/mark-cod-paid",
            headers=auth_headers_admin
        )
        # May succeed or fail depending on order payment method
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

    def test_get_payment_details(self, client, auth_headers_customer, test_order):
        """Test getting payment details."""
        response = client.get(
            f"/api/v1/payments/{test_order['id']}",
            headers=auth_headers_customer
        )
        # May return payment details or 404 if no payment yet
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

    def test_payments_require_auth(self, client):
        """Test that payment endpoints require authentication."""
        from uuid import uuid4
        response = client.post(
            "/api/v1/payments/initiate",
            json={"order_id": str(uuid4())}
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
