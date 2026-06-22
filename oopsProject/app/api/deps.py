"""
API dependencies - re-export from core.dependencies for convenience.
"""
from app.core.dependencies import (
    get_current_user,
    get_current_active_user,
    get_optional_user,
    get_current_user_token,
    RoleChecker,
    require_customer,
    require_retailer,
    require_wholesaler,
    require_seller,
    require_admin,
)

__all__ = [
    "get_current_user",
    "get_current_active_user",
    "get_optional_user",
    "get_current_user_token",
    "RoleChecker",
    "require_customer",
    "require_retailer",
    "require_wholesaler",
    "require_seller",
    "require_admin",
]
