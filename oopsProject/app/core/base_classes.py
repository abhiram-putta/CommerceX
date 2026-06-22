"""
Abstract base classes for the application.
Provides foundation for OOP design patterns.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import Base

# Type variable for generic models
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(ABC, Generic[ModelType]):
    """
    Abstract base repository class.
    Implements common CRUD operations for database models.
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession) -> None:
        """
        Initialize repository.

        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db

    @abstractmethod
    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """Create a new record."""
        pass

    @abstractmethod
    async def get(self, id: UUID) -> Optional[ModelType]:
        """Get record by ID."""
        pass

    @abstractmethod
    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[ModelType]:
        """Get multiple records with pagination."""
        pass

    @abstractmethod
    async def update(self, id: UUID, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """Update record by ID."""
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Delete record by ID."""
        pass

    @abstractmethod
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count records with optional filters."""
        pass


class BaseService(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Abstract base service class.
    Implements business logic layer on top of repositories.
    """

    def __init__(self, repository: BaseRepository[ModelType]) -> None:
        """
        Initialize service.

        Args:
            repository: Repository instance
        """
        self.repository = repository

    @abstractmethod
    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create new entity."""
        pass

    @abstractmethod
    async def get(self, id: UUID) -> Optional[ModelType]:
        """Get entity by ID."""
        pass

    @abstractmethod
    async def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters: Any,
    ) -> List[ModelType]:
        """Get multiple entities with pagination."""
        pass

    @abstractmethod
    async def update(self, id: UUID, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        """Update entity by ID."""
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Delete entity by ID."""
        pass


class BaseMLModel(ABC):
    """
    Abstract base class for ML models.
    Provides common interface for machine learning models.
    """

    def __init__(self, model_path: Optional[str] = None) -> None:
        """
        Initialize ML model.

        Args:
            model_path: Path to saved model file
        """
        self.model_path = model_path
        self.model: Any = None
        self.is_trained = False

    @abstractmethod
    async def train(self, data: Any) -> None:
        """Train the model with given data."""
        pass

    @abstractmethod
    async def predict(self, input_data: Any) -> Any:
        """Make predictions using the model."""
        pass

    @abstractmethod
    async def save(self, path: str) -> None:
        """Save model to disk."""
        pass

    @abstractmethod
    async def load(self, path: str) -> None:
        """Load model from disk."""
        pass

    @abstractmethod
    def evaluate(self, test_data: Any) -> Dict[str, float]:
        """Evaluate model performance."""
        pass


class BaseCeleryTask(ABC):
    """
    Abstract base class for Celery tasks.
    Provides common interface for background tasks.
    """

    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the task."""
        pass

    @abstractmethod
    def on_success(self, result: Any) -> None:
        """Callback on task success."""
        pass

    @abstractmethod
    def on_failure(self, exc: Exception) -> None:
        """Callback on task failure."""
        pass
