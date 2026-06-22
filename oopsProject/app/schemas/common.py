"""
Common schemas used across the application.
"""
from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

from app.utils.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""

    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(
        default=DEFAULT_PAGE_SIZE,
        ge=1,
        le=MAX_PAGE_SIZE,
        description="Items per page"
    )

    @property
    def skip(self) -> int:
        """Calculate skip value for database query."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get limit value for database query."""
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""

    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse[T]":
        """
        Create paginated response.

        Args:
            items: List of items
            total: Total count of items
            page: Current page number
            page_size: Items per page

        Returns:
            PaginatedResponse instance
        """
        total_pages = (total + page_size - 1) // page_size
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


class MessageResponse(BaseModel):
    """Generic message response."""

    message: str
    success: bool = True
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Error response schema."""

    message: str
    error_code: Optional[str] = None
    details: Optional[dict] = None


class SearchParams(BaseModel):
    """Search parameters."""

    query: str = Field(..., min_length=2, description="Search query")
    category_id: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    brand: Optional[str] = None
    is_local: Optional[bool] = None
    region: Optional[str] = None
    sort_by: Optional[str] = Field(None, description="Sort field (price, rating, name)")
    sort_order: Optional[str] = Field("asc", description="Sort order (asc, desc)")
