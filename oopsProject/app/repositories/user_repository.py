"""
User repository for user-specific database operations.
"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.repositories.base_repository import CRUDRepository


class UserRepository(CRUDRepository[User]):
    """User repository with custom methods."""

    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize user repository.

        Args:
            db: Database session
        """
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            email: User email

        Returns:
            User instance or None
        """
        result = await self.db.execute(
            select(User)
            .where(User.email == email)
            .options(selectinload(User.profile))
        )
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> Optional[User]:
        """
        Get user by phone number.

        Args:
            phone: User phone number

        Returns:
            User instance or None
        """
        result = await self.db.execute(
            select(User)
            .where(User.phone == phone)
            .options(selectinload(User.profile))
        )
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """
        Check if email already exists.

        Args:
            email: Email to check

        Returns:
            True if exists, False otherwise
        """
        result = await self.db.execute(
            select(User.id).where(User.email == email)
        )
        return result.scalar_one_or_none() is not None

    async def phone_exists(self, phone: str) -> bool:
        """
        Check if phone number already exists.

        Args:
            phone: Phone number to check

        Returns:
            True if exists, False otherwise
        """
        result = await self.db.execute(
            select(User.id).where(User.phone == phone)
        )
        return result.scalar_one_or_none() is not None

    async def update_last_login(self, user_id: str) -> None:
        """
        Update user's last login timestamp.

        Args:
            user_id: User UUID
        """
        from datetime import datetime
        import pytz

        user = await self.get(user_id)
        if user:
            user.last_login = datetime.now(pytz.UTC)
            self.db.add(user)
            await self.db.flush()
