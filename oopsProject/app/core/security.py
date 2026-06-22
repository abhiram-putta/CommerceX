"""
Security module for JWT authentication and password hashing.
Integrate your existing JWT implementation here.
"""
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config.settings import get_settings
from app.core.exceptions import AuthenticationError
from app.schemas.user import TokenData
from app.utils.enums import UserRole

settings = get_settings()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityManager:
    """Security manager for authentication and authorization."""

    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against a hash.

        Args:
            plain_password: Plain text password
            hashed_password: Hashed password

        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(
        user_id: UUID,
        email: str,
        role: UserRole,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        Create JWT access token.

        Args:
            user_id: User UUID
            email: User email
            role: User role
            expires_delta: Optional custom expiration time

        Returns:
            JWT access token
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode = {
            "sub": str(user_id),
            "email": email,
            "role": role.value,
            "exp": expire,
            "type": "access",
        }

        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

        return encoded_jwt

    @staticmethod
    def create_refresh_token(
        user_id: UUID,
        email: str,
        role: UserRole,
    ) -> str:
        """
        Create JWT refresh token.

        Args:
            user_id: User UUID
            email: User email
            role: User role

        Returns:
            JWT refresh token
        """
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        to_encode = {
            "sub": str(user_id),
            "email": email,
            "role": role.value,
            "exp": expire,
            "type": "refresh",
        }

        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> TokenData:
        """
        Verify and decode JWT token.

        Args:
            token: JWT token

        Returns:
            TokenData with user information

        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )

            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            role: str = payload.get("role")

            if user_id is None or email is None:
                raise AuthenticationError("Invalid token")

            return TokenData(
                user_id=UUID(user_id),
                email=email,
                role=UserRole(role),
            )

        except JWTError:
            raise AuthenticationError("Could not validate credentials")


# Create global security manager instance
security = SecurityManager()


# Helper functions for backward compatibility
def hash_password(password: str) -> str:
    """Hash password wrapper."""
    return security.hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password wrapper."""
    return security.verify_password(plain_password, hashed_password)


def create_access_token(user_id: UUID, email: str, role: UserRole) -> str:
    """Create access token wrapper."""
    return security.create_access_token(user_id, email, role)


def create_refresh_token(user_id: UUID, email: str, role: UserRole) -> str:
    """Create refresh token wrapper."""
    return security.create_refresh_token(user_id, email, role)


def verify_token(token: str) -> TokenData:
    """Verify token wrapper."""
    return security.verify_token(token)
