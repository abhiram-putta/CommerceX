"""
Analytics models for search queries and user behavior.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import ARRAY, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped

from app.models.base import BaseModel


class SearchQuery(BaseModel):
    """
    Search query model for tracking and analyzing user searches.
    """

    __tablename__ = "search_queries"

    # User (optional for guest searches)
    user_id: Mapped[Optional[UUID]] = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Query details
    query_text: Mapped[str] = Column(String, nullable=False, index=True)
    filters_applied: Mapped[dict] = Column(JSONB, default={}, nullable=False)
    results_count: Mapped[int] = Column(Integer, nullable=False)
    clicked_product_ids: Mapped[list] = Column(ARRAY(UUID(as_uuid=True)), default=[], nullable=False)

    # Session tracking
    session_id: Mapped[str] = Column(String(255), nullable=False, index=True)
    timestamp: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<SearchQuery(query={self.query_text}, results={self.results_count})>"
