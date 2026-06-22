"""
User management endpoints.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.config.database import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.common import MessageResponse
from app.schemas.user import UserProfileResponse, UserProfileUpdate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """
    Get user service dependency.

    Args:
        db: Database session

    Returns:
        UserService instance
    """
    user_repository = UserRepository(db)
    return UserService(user_repository)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get currently authenticated user's profile.",
)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """
    Get current user profile.

    Requires authentication (Bearer token).

    Returns complete user profile with all details.
    """
    return UserResponse.model_validate(current_user)


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user",
    description="Update currently authenticated user's basic information.",
)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """
    Update current user.

    Requires authentication (Bearer token).

    - **phone**: Optional phone number update
    - **is_active**: Optional account status update
    """
    updated_user = await user_service.update(current_user.id, user_update)
    return UserResponse.model_validate(updated_user)


@router.delete(
    "/me",
    response_model=MessageResponse,
    summary="Deactivate account",
    description="Deactivate currently authenticated user's account.",
)
async def deactivate_account(
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> MessageResponse:
    """
    Deactivate current user account.

    Requires authentication (Bearer token).

    This performs a soft delete (sets is_active=False).
    """
    await user_service.delete(current_user.id)
    return MessageResponse(message="Account deactivated successfully")


@router.put(
    "/me/profile",
    response_model=UserProfileResponse,
    summary="Update user profile",
    description="Update currently authenticated user's extended profile information.",
)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
) -> UserProfileResponse:
    """
    Update user profile.

    Requires authentication (Bearer token).

    Update extended profile information including:
    - Personal details (name, DOB, gender)
    - Address information
    - Business details (for retailers/wholesalers)
    - Preferences (for ML personalization)
    """
    profile = await user_service.update_profile(current_user.id, profile_update)
    return UserProfileResponse.model_validate(profile)


@router.get(
    "/me/statistics",
    response_model=dict,
    summary="Get user statistics",
    description="Get statistics and activity summary for current user.",
)
async def get_user_statistics(
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """
    Get user statistics.

    Requires authentication (Bearer token).

    Returns activity statistics including:
    - Total orders
    - Total spent
    - Total reviews
    - Profile completion percentage
    """
    # TODO: Implement actual statistics calculation
    return {
        "total_orders": 0,
        "total_spent": 0.0,
        "total_reviews": 0,
        "profile_completion": current_user.profile_completion,
        "member_since": current_user.created_at,
        "last_login": current_user.last_login,
    }
