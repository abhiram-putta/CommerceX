"""
Dependency injection for FastAPI routes.
"""
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import verify_token
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import TokenData
from app.utils.enums import UserRole

# HTTP Bearer security scheme
security_scheme = HTTPBearer()


async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
) -> TokenData:
    """
    Get current user from JWT token.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        TokenData with user information

    Raises:
        HTTPException: If token is invalid
    """
    try:
        token = credentials.credentials
        token_data = verify_token(token)
        return token_data
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token_data: TokenData = Depends(get_current_user_token),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current authenticated user from database.

    Args:
        token_data: Token data from JWT
        db: Database session

    Returns:
        User instance

    Raises:
        HTTPException: If user not found or inactive
    """
    user_repo = UserRepository(db)
    user = await user_repo.get(token_data.user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user.

    Args:
        current_user: Current user from token

    Returns:
        User instance

    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


class RoleChecker:
    """Role-based access control checker."""

    def __init__(self, allowed_roles: list[UserRole]) -> None:
        """
        Initialize role checker.

        Args:
            allowed_roles: List of allowed user roles
        """
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_active_user)) -> User:
        """
        Check if user has required role.

        Args:
            current_user: Current authenticated user

        Returns:
            User instance if authorized

        Raises:
            HTTPException: If user doesn't have required role
        """
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{current_user.role}' not authorized for this operation",
            )
        return current_user


# Common role checkers
require_customer = RoleChecker([UserRole.CUSTOMER, UserRole.RETAILER, UserRole.WHOLESALER])
require_retailer = RoleChecker([UserRole.RETAILER])
require_wholesaler = RoleChecker([UserRole.WHOLESALER])
require_seller = RoleChecker([UserRole.RETAILER, UserRole.WHOLESALER])
require_admin = RoleChecker([UserRole.ADMIN])


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise None.
    Useful for endpoints that work both authenticated and unauthenticated.

    Args:
        credentials: Optional HTTP authorization credentials
        db: Database session

    Returns:
        User instance or None
    """
    if not credentials:
        return None

    try:
        token = credentials.credentials
        token_data = verify_token(token)
        user_repo = UserRepository(db)
        user = await user_repo.get(token_data.user_id)
        return user if user and user.is_active else None
    except Exception:
        return None
