"""
Custom exception hierarchy for the application.
Provides structured error handling with HTTP status codes.
"""
from typing import Any, Dict, Optional


class SmartException(Exception):
    """Base exception class for all application exceptions."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize exception.

        Args:
            message: Error message
            status_code: HTTP status code
            details: Additional error details
        """
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(SmartException):
    """Validation error exception."""

    def __init__(self, message: str = "Validation error", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, status_code=422, details=details)


class AuthenticationError(SmartException):
    """Authentication error exception."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message=message, status_code=401)


class AuthorizationError(SmartException):
    """Authorization error exception."""

    def __init__(self, message: str = "Permission denied") -> None:
        super().__init__(message=message, status_code=403)


class NotFoundError(SmartException):
    """Resource not found exception."""

    def __init__(self, message: str = "Resource not found", resource: Optional[str] = None) -> None:
        details = {"resource": resource} if resource else {}
        super().__init__(message=message, status_code=404, details=details)


class ConflictError(SmartException):
    """Conflict error exception."""

    def __init__(self, message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, status_code=409, details=details)


class BadRequestError(SmartException):
    """Bad request error exception."""

    def __init__(self, message: str = "Bad request", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, status_code=400, details=details)


class DatabaseError(SmartException):
    """Database operation error exception."""

    def __init__(self, message: str = "Database error", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, status_code=500, details=details)


class ExternalServiceError(SmartException):
    """External service error exception."""

    def __init__(
        self,
        message: str = "External service error",
        service: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        error_details = details or {}
        if service:
            error_details["service"] = service
        super().__init__(message=message, status_code=503, details=error_details)


class PaymentError(SmartException):
    """Payment processing error exception."""

    def __init__(self, message: str = "Payment processing failed", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, status_code=402, details=details)


class InsufficientStockError(SmartException):
    """Insufficient stock error exception."""

    def __init__(
        self,
        message: str = "Insufficient stock",
        product_id: Optional[str] = None,
        available: Optional[int] = None,
        requested: Optional[int] = None,
    ) -> None:
        details = {}
        if product_id:
            details["product_id"] = product_id
        if available is not None:
            details["available"] = available
        if requested is not None:
            details["requested"] = requested
        super().__init__(message=message, status_code=409, details=details)


class RateLimitError(SmartException):
    """Rate limit exceeded error exception."""

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        super().__init__(message=message, status_code=429)


class FileUploadError(SmartException):
    """File upload error exception."""

    def __init__(self, message: str = "File upload failed", details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message=message, status_code=400, details=details)


class MLModelError(SmartException):
    """ML model error exception."""

    def __init__(
        self,
        message: str = "ML model error",
        model: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        error_details = details or {}
        if model:
            error_details["model"] = model
        super().__init__(message=message, status_code=500, details=error_details)
