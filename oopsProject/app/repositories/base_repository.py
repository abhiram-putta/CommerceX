"""
Concrete implementation of base repository with common CRUD operations.
"""
from typing import Any, Dict, Generic, List, Optional, Type
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_classes import BaseRepository, ModelType
from app.core.exceptions import DatabaseError, NotFoundError
from app.utils.logger import get_logger

logger = get_logger(__name__)


class CRUDRepository(BaseRepository[ModelType], Generic[ModelType]):
    """
    Concrete repository implementation with CRUD operations.
    Inherit from this class to create specific repositories.
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession) -> None:
        """
        Initialize repository.

        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        super().__init__(model, db)

    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """
        Create a new record.

        Args:
            obj_in: Dictionary with model data

        Returns:
            Created model instance

        Raises:
            DatabaseError: If creation fails
        """
        try:
            db_obj = self.model(**obj_in)
            self.db.add(db_obj)
            await self.db.flush()
            await self.db.refresh(db_obj)
            logger.info(f"Created {self.model.__name__} with id={db_obj.id}")
            return db_obj
        except Exception as e:
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise DatabaseError(f"Failed to create {self.model.__name__}")

    async def get(self, id: UUID) -> Optional[ModelType]:
        """
        Get record by ID.

        Args:
            id: Record UUID

        Returns:
            Model instance or None if not found
        """
        try:
            result = await self.db.execute(
                select(self.model).where(self.model.id == id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} with id={id}: {e}")
            return None

    async def get_or_404(self, id: UUID) -> ModelType:
        """
        Get record by ID or raise NotFoundError.

        Args:
            id: Record UUID

        Returns:
            Model instance

        Raises:
            NotFoundError: If record not found
        """
        obj = await self.get(id)
        if not obj:
            raise NotFoundError(
                f"{self.model.__name__} not found",
                resource=self.model.__name__,
            )
        return obj

    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[ModelType]:
        """
        Get multiple records with pagination and filters.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Optional filters as key-value pairs

        Returns:
            List of model instances
        """
        try:
            query = select(self.model)

            # Apply filters if provided
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key) and value is not None:
                        query = query.where(getattr(self.model, key) == value)

            # Apply pagination
            query = query.offset(skip).limit(limit)

            result = await self.db.execute(query)
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting {self.model.__name__} records: {e}")
            return []

    async def update(self, id: UUID, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """
        Update record by ID.

        Args:
            id: Record UUID
            obj_in: Dictionary with fields to update

        Returns:
            Updated model instance or None if not found

        Raises:
            DatabaseError: If update fails
        """
        try:
            db_obj = await self.get(id)
            if not db_obj:
                return None

            # Update fields
            for field, value in obj_in.items():
                if hasattr(db_obj, field) and value is not None:
                    setattr(db_obj, field, value)

            self.db.add(db_obj)
            await self.db.flush()
            await self.db.refresh(db_obj)
            logger.info(f"Updated {self.model.__name__} with id={id}")
            return db_obj
        except Exception as e:
            logger.error(f"Error updating {self.model.__name__} with id={id}: {e}")
            raise DatabaseError(f"Failed to update {self.model.__name__}")

    async def delete(self, id: UUID) -> bool:
        """
        Delete record by ID.

        Args:
            id: Record UUID

        Returns:
            True if deleted, False if not found

        Raises:
            DatabaseError: If deletion fails
        """
        try:
            db_obj = await self.get(id)
            if not db_obj:
                return False

            await self.db.delete(db_obj)
            await self.db.flush()
            logger.info(f"Deleted {self.model.__name__} with id={id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting {self.model.__name__} with id={id}: {e}")
            raise DatabaseError(f"Failed to delete {self.model.__name__}")

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count records with optional filters.

        Args:
            filters: Optional filters as key-value pairs

        Returns:
            Number of records
        """
        try:
            query = select(func.count()).select_from(self.model)

            # Apply filters if provided
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key) and value is not None:
                        query = query.where(getattr(self.model, key) == value)

            result = await self.db.execute(query)
            return result.scalar_one()
        except Exception as e:
            logger.error(f"Error counting {self.model.__name__} records: {e}")
            return 0

    async def exists(self, id: UUID) -> bool:
        """
        Check if record exists by ID.

        Args:
            id: Record UUID

        Returns:
            True if exists, False otherwise
        """
        result = await self.get(id)
        return result is not None
