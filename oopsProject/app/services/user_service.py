"""
User service for user management business logic.
"""
from typing import Optional
from uuid import UUID

from app.core.base_classes import BaseService
from app.core.exceptions import ConflictError, NotFoundError
from app.core.security import hash_password, verify_password
from app.models.user import User, UserProfile
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserProfileUpdate, UserUpdate
from app.utils.helpers import get_utc_now
from app.utils.logger import get_logger

logger = get_logger(__name__)


class UserService(BaseService[User, UserCreate, UserUpdate]):
    """User service with business logic for user management."""

    def __init__(self, repository: UserRepository) -> None:
        """
        Initialize user service.

        Args:
            repository: User repository instance
        """
        super().__init__(repository)
        self.repository = repository

    async def create(self, obj_in: UserCreate) -> User:
        """
        Create a new user.

        Args:
            obj_in: User creation data

        Returns:
            Created user instance

        Raises:
            ConflictError: If email or phone already exists
        """
        # Check if email already exists
        if await self.repository.email_exists(obj_in.email):
            raise ConflictError("Email already registered")

        # Check if phone already exists
        if obj_in.phone and await self.repository.phone_exists(obj_in.phone):
            raise ConflictError("Phone number already registered")

        # Hash password
        hashed_password = hash_password(obj_in.password)

        # Prepare user data
        user_data = obj_in.model_dump(exclude={'password', 'full_name'})
        user_data['password_hash'] = hashed_password

        # Create user
        user = await self.repository.create(user_data)

        # Create user profile
        profile_data = {
            'user_id': user.id,
            'full_name': obj_in.full_name,
        }
        profile = UserProfile(**profile_data)
        self.repository.db.add(profile)
        await self.repository.db.flush()

        # Refresh to get profile relationship
        await self.repository.db.refresh(user)

        logger.info(f"User created: {user.email}")

        # TODO: Send verification email (Celery task)
        # send_verification_email.delay(user.id, user.email)

        return user

    async def get(self, id: UUID) -> Optional[User]:
        """
        Get user by ID.

        Args:
            id: User UUID

        Returns:
            User instance or None
        """
        return await self.repository.get(id)

    async def get_multi(self, skip: int = 0, limit: int = 100, **filters) -> list[User]:
        """
        Get multiple users.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records
            **filters: Additional filters

        Returns:
            List of users
        """
        return await self.repository.get_multi(skip=skip, limit=limit, filters=filters)

    async def update(self, id: UUID, obj_in: UserUpdate) -> Optional[User]:
        """
        Update user.

        Args:
            id: User UUID
            obj_in: User update data

        Returns:
            Updated user instance

        Raises:
            ConflictError: If phone already exists
        """
        # Check if phone already exists (if updating phone)
        if obj_in.phone:
            existing_user = await self.repository.get_by_phone(obj_in.phone)
            if existing_user and existing_user.id != id:
                raise ConflictError("Phone number already registered")

        # Update user
        update_data = obj_in.model_dump(exclude_unset=True)
        user = await self.repository.update(id, update_data)

        if user:
            logger.info(f"User updated: {user.email}")

        return user

    async def delete(self, id: UUID) -> bool:
        """
        Delete user (soft delete by setting is_active=False).

        Args:
            id: User UUID

        Returns:
            True if deleted, False otherwise
        """
        user = await self.repository.get(id)
        if not user:
            return False

        # Soft delete
        await self.repository.update(id, {'is_active': False})
        logger.info(f"User deactivated: {user.email}")
        return True

    async def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.

        Args:
            email: User email
            password: Plain text password

        Returns:
            User instance if authenticated, None otherwise
        """
        user = await self.repository.get_by_email(email)

        if not user:
            logger.warning(f"Authentication failed: user not found - {email}")
            return None

        if not user.is_active:
            logger.warning(f"Authentication failed: user inactive - {email}")
            return None

        if not verify_password(password, user.password_hash):
            logger.warning(f"Authentication failed: invalid password - {email}")
            return None

        # Update last login
        await self.repository.update_last_login(user.id)

        logger.info(f"User authenticated: {email}")
        return user

    async def update_profile(
        self,
        user_id: UUID,
        profile_data: UserProfileUpdate,
    ) -> Optional[UserProfile]:
        """
        Update user profile.

        Args:
            user_id: User UUID
            profile_data: Profile update data

        Returns:
            Updated profile instance

        Raises:
            NotFoundError: If user not found
        """
        user = await self.repository.get(user_id)
        if not user:
            raise NotFoundError("User not found")

        if not user.profile:
            # Create profile if doesn't exist
            profile = UserProfile(user_id=user_id)
            self.repository.db.add(profile)
            await self.repository.db.flush()
        else:
            profile = user.profile

        # Update profile fields
        update_data = profile_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(profile, field):
                setattr(profile, field, value)

        self.repository.db.add(profile)
        await self.repository.db.flush()
        await self.repository.db.refresh(profile)

        logger.info(f"Profile updated for user: {user.email}")

        return profile

    async def verify_email(self, user_id: UUID) -> bool:
        """
        Verify user's email.

        Args:
            user_id: User UUID

        Returns:
            True if verified, False otherwise
        """
        user = await self.repository.get(user_id)
        if not user:
            return False

        await self.repository.update(user_id, {'email_verified': True})
        logger.info(f"Email verified: {user.email}")
        return True

    async def verify_phone(self, user_id: UUID) -> bool:
        """
        Verify user's phone number.

        Args:
            user_id: User UUID

        Returns:
            True if verified, False otherwise
        """
        user = await self.repository.get(user_id)
        if not user:
            return False

        await self.repository.update(user_id, {'phone_verified': True})
        logger.info(f"Phone verified: {user.phone}")
        return True
