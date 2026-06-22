"""
Base model class with common fields and functionality.
"""
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_mixin, declared_attr

from app.config.database import Base as DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all database models."""

    __abstract__ = True


@declarative_mixin
class TimestampMixin:
    """
    Mixin to add created_at and updated_at timestamp fields.
    Automatically managed by the database.
    """

    @declared_attr
    def created_at(cls):
        """Timestamp when record was created."""
        return Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )

    @declared_attr
    def updated_at(cls):
        """Timestamp when record was last updated."""
        return Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )


@declarative_mixin
class UUIDMixin:
    """Mixin to add UUID primary key."""

    @declared_attr
    def id(cls):
        """UUID primary key."""
        return Column(
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            unique=True,
            nullable=False,
        )


class BaseModel(Base, UUIDMixin, TimestampMixin):
    """
    Base model class with UUID primary key and timestamps.
    All models should inherit from this class.
    """

    __abstract__ = True
    __allow_unmapped__ = True  # Allow legacy Column definitions without Mapped[]

    def to_dict(self) -> dict[str, Any]:
        """
        Convert model instance to dictionary.

        Returns:
            Dictionary representation of the model
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def __repr__(self) -> str:
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"
