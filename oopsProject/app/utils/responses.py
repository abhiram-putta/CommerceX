"""
Standardized response utilities for API endpoints.
"""
from typing import Any, Dict, List, Optional

from fastapi import status
from fastapi.responses import JSONResponse


class APIResponse:
    """Utility class for creating standardized API responses."""

    @staticmethod
    def success(
        data: Any = None,
        message: str = "Success",
        status_code: int = status.HTTP_200_OK,
        meta: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """
        Create success response.

        Args:
            data: Response data
            message: Success message
            status_code: HTTP status code
            meta: Additional metadata

        Returns:
            JSONResponse with success format
        """
        content = {
            "success": True,
            "message": message,
            "data": data
        }

        if meta:
            content["meta"] = meta

        return JSONResponse(status_code=status_code, content=content)

    @staticmethod
    def error(
        message: str = "An error occurred",
        errors: Optional[List[Dict[str, Any]]] = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: Optional[str] = None
    ) -> JSONResponse:
        """
        Create error response.

        Args:
            message: Error message
            errors: List of detailed errors
            status_code: HTTP status code
            error_code: Application-specific error code

        Returns:
            JSONResponse with error format
        """
        content = {
            "success": False,
            "message": message,
        }

        if errors:
            content["errors"] = errors

        if error_code:
            content["error_code"] = error_code

        return JSONResponse(status_code=status_code, content=content)

    @staticmethod
    def created(
        data: Any = None,
        message: str = "Resource created successfully",
        resource_id: Optional[str] = None
    ) -> JSONResponse:
        """
        Create 201 Created response.

        Args:
            data: Response data
            message: Success message
            resource_id: ID of created resource

        Returns:
            JSONResponse with 201 status
        """
        meta = {"resource_id": resource_id} if resource_id else None
        return APIResponse.success(
            data=data,
            message=message,
            status_code=status.HTTP_201_CREATED,
            meta=meta
        )

    @staticmethod
    def no_content(message: str = "Operation successful") -> JSONResponse:
        """
        Create 204 No Content response.

        Args:
            message: Success message

        Returns:
            JSONResponse with 204 status
        """
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=None
        )

    @staticmethod
    def not_found(
        message: str = "Resource not found",
        resource: Optional[str] = None
    ) -> JSONResponse:
        """
        Create 404 Not Found response.

        Args:
            message: Error message
            resource: Resource type that wasn't found

        Returns:
            JSONResponse with 404 status
        """
        errors = [{"resource": resource}] if resource else None
        return APIResponse.error(
            message=message,
            errors=errors,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND"
        )

    @staticmethod
    def unauthorized(
        message: str = "Authentication required",
        error_code: str = "UNAUTHORIZED"
    ) -> JSONResponse:
        """
        Create 401 Unauthorized response.

        Args:
            message: Error message
            error_code: Error code

        Returns:
            JSONResponse with 401 status
        """
        return APIResponse.error(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=error_code
        )

    @staticmethod
    def forbidden(
        message: str = "Access forbidden",
        error_code: str = "FORBIDDEN"
    ) -> JSONResponse:
        """
        Create 403 Forbidden response.

        Args:
            message: Error message
            error_code: Error code

        Returns:
            JSONResponse with 403 status
        """
        return APIResponse.error(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=error_code
        )

    @staticmethod
    def validation_error(
        message: str = "Validation failed",
        errors: List[Dict[str, Any]] = None
    ) -> JSONResponse:
        """
        Create 422 Validation Error response.

        Args:
            message: Error message
            errors: List of validation errors

        Returns:
            JSONResponse with 422 status
        """
        return APIResponse.error(
            message=message,
            errors=errors,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR"
        )

    @staticmethod
    def conflict(
        message: str = "Resource conflict",
        details: Optional[Dict[str, Any]] = None
    ) -> JSONResponse:
        """
        Create 409 Conflict response.

        Args:
            message: Error message
            details: Conflict details

        Returns:
            JSONResponse with 409 status
        """
        errors = [details] if details else None
        return APIResponse.error(
            message=message,
            errors=errors,
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT"
        )

    @staticmethod
    def paginated(
        data: List[Any],
        total: int,
        page: int = 1,
        page_size: int = 20,
        message: str = "Success"
    ) -> JSONResponse:
        """
        Create paginated response.

        Args:
            data: List of items for current page
            total: Total number of items
            page: Current page number
            page_size: Items per page
            message: Success message

        Returns:
            JSONResponse with pagination metadata
        """
        total_pages = (total + page_size - 1) // page_size

        meta = {
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }

        return APIResponse.success(
            data=data,
            message=message,
            meta=meta
        )


def format_validation_errors(errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format Pydantic validation errors for API response.

    Args:
        errors: Raw Pydantic validation errors

    Returns:
        Formatted error list
    """
    formatted_errors = []

    for error in errors:
        formatted_error = {
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        }
        formatted_errors.append(formatted_error)

    return formatted_errors
