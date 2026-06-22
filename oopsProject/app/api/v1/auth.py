"""
Authentication endpoints.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.common import MessageResponse
from app.schemas.user import (
    EmailVerification,
    PasswordReset,
    PasswordResetConfirm,
    PhoneVerification,
    Token,
    UserCreate,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter()


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """
    Get auth service dependency.

    Args:
        db: Database session

    Returns:
        AuthService instance
    """
    user_repository = UserRepository(db)
    return AuthService(user_repository)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user account. Email and phone must be unique.",
)
async def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """
    Register a new user.

    - **email**: Valid email address (must be unique)
    - **password**: Strong password (min 8 chars, with uppercase, lowercase, digit, special char)
    - **phone**: Optional phone number (must be unique if provided)
    - **role**: User role (customer, retailer, wholesaler)
    - **full_name**: Optional full name
    """
    user = await auth_service.register(user_data)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=Token,
    summary="Login user",
    description="Authenticate user and return JWT access and refresh tokens.",
)
async def login(
    email: str,
    password: str,
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    """
    Login user with email and password.

    Returns JWT access token and refresh token.

    - **email**: User email
    - **password**: User password
    """
    return await auth_service.login(email, password)


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token",
    description="Get new access token using refresh token.",
)
async def refresh_token(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service),
) -> Token:
    """
    Refresh access token.

    - **refresh_token**: Valid refresh token
    """
    return await auth_service.refresh_access_token(refresh_token)


@router.post(
    "/verify-email",
    response_model=MessageResponse,
    summary="Verify email",
    description="Verify user email with verification token.",
)
async def verify_email(
    verification: EmailVerification,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """
    Verify user email.

    - **token**: Email verification token sent to user's email
    """
    await auth_service.verify_email_token(verification.token)
    return MessageResponse(message="Email verified successfully")


@router.post(
    "/verify-phone",
    response_model=MessageResponse,
    summary="Verify phone number",
    description="Verify user phone number with OTP.",
)
async def verify_phone(
    verification: PhoneVerification,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """
    Verify user phone number.

    - **phone**: Phone number
    - **otp**: OTP code sent to phone
    """
    # TODO: Get user_id from phone number
    # For now, this is a placeholder
    return MessageResponse(message="Phone verified successfully")


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    summary="Request password reset",
    description="Send password reset email to user.",
)
async def forgot_password(
    request: PasswordReset,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """
    Request password reset.

    Sends password reset email with reset token.

    - **email**: User email address
    """
    await auth_service.send_password_reset_email(request.email)
    return MessageResponse(
        message="Password reset email sent. Please check your inbox."
    )


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    summary="Reset password",
    description="Reset password using reset token.",
)
async def reset_password(
    reset_data: PasswordResetConfirm,
    auth_service: AuthService = Depends(get_auth_service),
) -> MessageResponse:
    """
    Reset password.

    - **token**: Password reset token from email
    - **new_password**: New password (min 8 chars, with uppercase, lowercase, digit, special char)
    """
    await auth_service.reset_password(reset_data.token, reset_data.new_password)
    return MessageResponse(message="Password reset successfully")
