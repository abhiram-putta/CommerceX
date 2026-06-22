"""
User and authentication schemas.
"""
from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.base import BaseResponseSchema, BaseSchema
from app.utils.enums import Gender, UserRole
from app.utils.validators import validate_password_strength, validate_phone_number


class UserBase(BaseSchema):
    """Base user schema."""

    email: EmailStr


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8, max_length=128)
    phone: Optional[str] = None
    role: UserRole = Field(default=UserRole.CUSTOMER)
    full_name: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not validate_password_strength(v):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, one digit, and one special character"
            )
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number."""
        if v and not validate_phone_number(v):
            raise ValueError("Invalid phone number")
        return v


class UserLogin(BaseSchema):
    """User login schema."""

    email: EmailStr
    password: str


class UserUpdate(BaseSchema):
    """User update schema."""

    phone: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate phone number."""
        if v and not validate_phone_number(v):
            raise ValueError("Invalid phone number")
        return v


class UserProfileUpdate(BaseSchema):
    """User profile update schema."""

    full_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[Gender] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None
    business_name: Optional[str] = None
    business_license: Optional[str] = None
    gst_number: Optional[str] = None
    business_type: Optional[str] = None
    business_description: Optional[str] = None
    preferences: Optional[dict] = None


class UserProfileResponse(BaseResponseSchema):
    """User profile response schema."""

    user_id: UUID
    full_name: Optional[str] = None
    profile_image_url: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str
    pincode: Optional[str] = None
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    preferences: dict


class UserResponse(BaseResponseSchema):
    """User response schema."""

    email: str
    phone: Optional[str] = None
    role: UserRole
    is_active: bool
    is_verified: bool
    email_verified: bool
    phone_verified: bool
    profile_completion: float
    last_login: Optional[datetime] = None
    profile: Optional[UserProfileResponse] = None


class Token(BaseSchema):
    """JWT token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseSchema):
    """JWT token payload data."""

    user_id: UUID
    email: str
    role: UserRole


class PasswordReset(BaseSchema):
    """Password reset request schema."""

    email: EmailStr


class PasswordResetConfirm(BaseSchema):
    """Password reset confirmation schema."""

    token: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not validate_password_strength(v):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, one digit, and one special character"
            )
        return v


class EmailVerification(BaseSchema):
    """Email verification schema."""

    token: str


class PhoneVerification(BaseSchema):
    """Phone verification schema."""

    phone: str
    otp: str
