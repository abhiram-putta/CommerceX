"""
Tests for authentication endpoints.
"""
import pytest
from fastapi import status


@pytest.mark.unit
class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_register_customer(self, client):
        """Test customer registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@test.com",
                "username": "newuser",
                "password": "SecurePass123!",
                "full_name": "New User",
                "role": "CUSTOMER"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "newuser@test.com"
        assert data["username"] == "newuser"
        assert "password" not in data

    def test_register_duplicate_email(self, client, test_customer):
        """Test registration with duplicate email."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "customer@test.com",
                "username": "anotheruser",
                "password": "SecurePass123!",
                "full_name": "Another User",
                "role": "CUSTOMER"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_success(self, client, test_customer):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "customer@test.com",
                "password": "testpass123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client, test_customer):
        """Test login with invalid credentials."""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "customer@test.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user(self, client, auth_headers_customer):
        """Test get current user."""
        response = client.get(
            "/api/v1/auth/me",
            headers=auth_headers_customer
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "customer@test.com"

    def test_get_current_user_unauthorized(self, client):
        """Test get current user without auth."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token(self, client, test_customer):
        """Test token refresh."""
        # First login to get tokens
        login_response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "customer@test.com",
                "password": "testpass123"
            }
        )
        refresh_token = login_response.json()["refresh_token"]

        # Refresh token
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_logout(self, client, auth_headers_customer):
        """Test logout."""
        response = client.post(
            "/api/v1/auth/logout",
            headers=auth_headers_customer
        )
        assert response.status_code == status.HTTP_200_OK
