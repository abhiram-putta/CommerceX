"""
Authentication service for handling auth operations.
"""
from datetime import timedelta
from typing import Optional
from uuid import UUID

from app.core.exceptions import AuthenticationError, NotFoundError
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import Token, TokenData, UserCreate
from app.services.user_service import UserService
from app.utils.helpers import add_minutes, generate_random_string, get_utc_now
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AuthService:
    """Authentication service."""

    def __init__(self, user_repository: UserRepository) -> None:
        """
        Initialize auth service.

        Args:
            user_repository: User repository instance
        """
        self.user_repository = user_repository
        self.user_service = UserService(user_repository)

    async def register(self, user_data: UserCreate) -> User:
        """
        Register a new user.

        Args:
            user_data: User registration data

        Returns:
            Created user instance
        """
        user = await self.user_service.create(user_data)
        logger.info(f"User registered: {user.email}")
        return user

    async def login(self, email: str, password: str) -> Token:
        """
        Login user and return JWT tokens.

        Args:
            email: User email
            password: User password

        Returns:
            JWT tokens (access and refresh)

        Raises:
            AuthenticationError: If credentials are invalid
        """
        user = await self.user_service.authenticate(email, password)

        if not user:
            raise AuthenticationError("Invalid email or password")

        # Create tokens
        access_token = create_access_token(user.id, user.email, user.role)
        refresh_token = create_refresh_token(user.id, user.email, user.role)

        logger.info(f"User logged in: {user.email}")

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def refresh_access_token(self, refresh_token: str) -> Token:
        """
        Refresh access token using refresh token.

        Args:
            refresh_token: Refresh token

        Returns:
            New JWT tokens

        Raises:
            AuthenticationError: If refresh token is invalid
        """
        try:
            token_data = verify_token(refresh_token)
        except AuthenticationError:
            raise AuthenticationError("Invalid refresh token")

        # Get user
        user = await self.user_repository.get(token_data.user_id)
        if not user or not user.is_active:
            raise AuthenticationError("Invalid refresh token")

        # Create new tokens
        access_token = create_access_token(user.id, user.email, user.role)
        new_refresh_token = create_refresh_token(user.id, user.email, user.role)

        logger.info(f"Token refreshed for user: {user.email}")

        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        )

    async def verify_email_token(self, token: str) -> bool:
        """
        Verify email verification token.

        Args:
            token: Email verification token

        Returns:
            True if verified successfully

        Raises:
            AuthenticationError: If token is invalid
        """
        # TODO: Implement proper email verification with token storage
        # For now, just decode and verify
        try:
            token_data = verify_token(token)
            await self.user_service.verify_email(token_data.user_id)
            return True
        except Exception as e:
            logger.error(f"Email verification failed: {e}")
            raise AuthenticationError("Invalid verification token")

    async def verify_phone_otp(self, user_id: UUID, otp: str) -> bool:
        """
        Verify phone OTP.

        Args:
            user_id: User UUID
            otp: OTP code

        Returns:
            True if verified successfully

        Raises:
            AuthenticationError: If OTP is invalid
        """
        # TODO: Implement proper OTP verification with Redis storage
        # For now, just verify the user exists
        user = await self.user_repository.get(user_id)
        if not user:
            raise NotFoundError("User not found")

        # In production, verify OTP from Redis
        # For now, just mark as verified
        await self.user_service.verify_phone(user_id)
        logger.info(f"Phone verified for user: {user.email}")
        return True

    async def send_password_reset_email(self, email: str) -> bool:
        """
        Send password reset email.

        Args:
            email: User email

        Returns:
            True if email sent successfully

        Raises:
            NotFoundError: If user not found
        """
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise NotFoundError("User not found")

        # TODO: Generate reset token and send email via Celery
        # reset_token = generate_random_string(32)
        # Store in Redis with expiration
        # send_password_reset_email.delay(user.email, reset_token)

        logger.info(f"Password reset email sent to: {email}")
        return True

    async def reset_password(
        self,
        token: str,
        new_password: str,
    ) -> bool:
        """
        Reset password using reset token.

        Args:
            token: Password reset token
            new_password: New password

        Returns:
            True if password reset successfully

        Raises:
            AuthenticationError: If token is invalid
        """
        # TODO: Implement proper password reset with token verification
        # For now, just decode token and update password
        try:
            from app.core.security import hash_password

            token_data = verify_token(token)
            user = await self.user_repository.get(token_data.user_id)

            if not user:
                raise AuthenticationError("Invalid reset token")

            # Update password
            hashed_password = hash_password(new_password)
            await self.user_repository.update(
                user.id,
                {'password_hash': hashed_password},
            )

            logger.info(f"Password reset for user: {user.email}")
            return True

        except Exception as e:
            logger.error(f"Password reset failed: {e}")
            raise AuthenticationError("Invalid reset token")
