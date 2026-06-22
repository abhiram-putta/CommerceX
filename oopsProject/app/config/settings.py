"""
Application settings using Pydantic Settings.
Manages environment variables and configuration.
"""
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings class."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application Settings
    APP_NAME: str = Field(default="sMart Backend", description="Application name")
    APP_ENV: str = Field(default="development", description="Environment (development, staging, production)")
    DEBUG: bool = Field(default=True, description="Debug mode")
    API_V1_PREFIX: str = Field(default="/api/v1", description="API v1 route prefix")

    # Security
    SECRET_KEY: str = Field(..., description="Secret key for JWT encoding")
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Access token expiration in minutes")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token expiration in days")

    # CORS Settings
    ALLOWED_ORIGINS: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"],
        description="Comma-separated list of allowed origins"
    )
    ALLOWED_HOSTS: str = Field(default="*", description="Allowed hosts")

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse comma-separated CORS origins."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        elif isinstance(v, list):
            return v
        return v

    # Database Settings
    DATABASE_URL: str = Field(
        ...,
        description="Database URL (PostgreSQL or SQLite)"
    )
    DATABASE_POOL_SIZE: int = Field(default=20, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, description="Database max overflow connections")

    # Redis Settings
    REDIS_URL: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    REDIS_CACHE_TTL: int = Field(default=3600, description="Default cache TTL in seconds")

    # Celery Settings
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1", description="Celery broker URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/2", description="Celery result backend URL")

    # MinIO Settings (S3-compatible storage)
    MINIO_ENDPOINT: str = Field(default="localhost:9000", description="MinIO endpoint")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin", description="MinIO access key")
    MINIO_SECRET_KEY: str = Field(default="minioadmin", description="MinIO secret key")
    MINIO_BUCKET_NAME: str = Field(default="smart-storage", description="MinIO bucket name")
    MINIO_SECURE: bool = Field(default=False, description="Use HTTPS for MinIO")

    # Email Settings (SMTP)
    SMTP_HOST: str = Field(default="smtp.gmail.com", description="SMTP server host")
    SMTP_PORT: int = Field(default=587, description="SMTP server port")
    SMTP_USER: str = Field(default="", description="SMTP username")
    SMTP_PASSWORD: str = Field(default="", description="SMTP password")
    FROM_EMAIL: str = Field(default="noreply@smart.com", description="From email address")
    FROM_NAME: str = Field(default="sMart", description="From email name")
    FRONTEND_URL: str = Field(default="http://localhost:3000", description="Frontend URL for email links")

    # SMS Settings (Twilio)
    TWILIO_ACCOUNT_SID: Optional[str] = Field(default=None, description="Twilio account SID")
    TWILIO_AUTH_TOKEN: Optional[str] = Field(default=None, description="Twilio auth token")
    TWILIO_PHONE_NUMBER: Optional[str] = Field(default=None, description="Twilio phone number")

    # Payment Gateway (Razorpay)
    RAZORPAY_KEY_ID: Optional[str] = Field(default=None, description="Razorpay key ID")
    RAZORPAY_KEY_SECRET: Optional[str] = Field(default=None, description="Razorpay key secret")
    RAZORPAY_WEBHOOK_SECRET: Optional[str] = Field(default=None, description="Razorpay webhook secret")

    # OAuth Settings
    GOOGLE_CLIENT_ID: Optional[str] = Field(default=None, description="Google OAuth client ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = Field(default=None, description="Google OAuth client secret")
    FACEBOOK_APP_ID: Optional[str] = Field(default=None, description="Facebook app ID")
    FACEBOOK_APP_SECRET: Optional[str] = Field(default=None, description="Facebook app secret")

    # ML Model Settings
    ML_MODEL_PATH: str = Field(default="./ml_models", description="Path to ML models directory")
    ML_RETRAIN_INTERVAL_HOURS: int = Field(default=24, description="ML model retraining interval")
    RECOMMENDATION_TOP_N: int = Field(default=10, description="Number of recommendations to return")
    SEARCH_EMBEDDING_MODEL: str = Field(
        default="all-MiniLM-L6-v2",
        description="Sentence transformer model for search"
    )

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, description="Rate limit per minute")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format (json or text)")

    # File Upload Settings
    MAX_UPLOAD_SIZE_MB: int = Field(default=10, description="Maximum file upload size in MB")
    ALLOWED_IMAGE_EXTENSIONS: List[str] = Field(
        default_factory=lambda: ["jpg", "jpeg", "png", "webp"],
        description="Comma-separated allowed image extensions"
    )

    @field_validator("ALLOWED_IMAGE_EXTENSIONS", mode="before")
    @classmethod
    def parse_image_extensions(cls, v):
        """Parse comma-separated image extensions."""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        elif isinstance(v, list):
            return v
        return v

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL (replace asyncpg with psycopg2 or aiosqlite)."""
        url = str(self.DATABASE_URL)
        if "postgresql+asyncpg://" in url:
            return url.replace("postgresql+asyncpg://", "postgresql://")
        elif "sqlite+aiosqlite:" in url:
            return url.replace("sqlite+aiosqlite:", "sqlite:")
        return url

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.APP_ENV.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.APP_ENV.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to ensure settings are loaded only once.
    """
    return Settings()
