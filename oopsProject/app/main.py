"""
Main FastAPI application initialization.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.config.database import close_db, init_db
from app.config.redis_client import redis_client
from app.config.settings import get_settings
from app.core.cache import cache_manager
from app.core.exceptions import SmartException
from app.core.middleware import (
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from app.core.rate_limiter import rate_limiter
from app.utils.logger import get_logger

# Import API routers
from app.api.v1.router import api_router

settings = get_settings()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Lifespan context manager for startup and shutdown events.

    Args:
        app: FastAPI application instance

    Yields:
        None
    """
    # Startup
    logger.info("Starting sMart Backend application")

    redis_connected = False

    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized successfully")

        # Try to connect to Redis (optional)
        try:
            await redis_client.connect()
            logger.info("Redis connected successfully")
            redis_connected = True

            # Connect rate limiter to Redis
            await rate_limiter.connect()
            logger.info("Rate limiter initialized successfully")

            # Connect cache manager to Redis
            await cache_manager.connect()
            logger.info("Cache manager initialized successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed, continuing without Redis: {e}")
            redis_connected = False

        # TODO: Load ML models
        # await load_ml_models()
        # logger.info("ML models loaded successfully")

        yield

    finally:
        # Shutdown
        logger.info("Shutting down sMart Backend application")

        # Close database connections
        await close_db()
        logger.info("Database connections closed")

        # Disconnect Redis, cache manager and rate limiter if connected
        if redis_connected:
            try:
                await rate_limiter.disconnect()
                await cache_manager.disconnect()
                await redis_client.disconnect()
                logger.info("Redis disconnected")
            except Exception as e:
                logger.warning(f"Error disconnecting Redis: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="ML-Powered E-commerce Backend Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    debug=settings.DEBUG,
)


# Add middlewares (order matters - first added is outermost)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(SmartException)
async def smart_exception_handler(request: Request, exc: SmartException) -> JSONResponse:
    """
    Handle custom application exceptions.

    Args:
        request: HTTP request
        exc: SmartException instance

    Returns:
        JSON response with error details
    """
    logger.error(
        "Application exception",
        exc_info=exc,
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    Handle Pydantic validation errors.

    Args:
        request: HTTP request
        exc: RequestValidationError instance

    Returns:
        JSON response with validation errors
    """
    logger.warning(
        "Validation error",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": exc.errors(),
        },
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "message": "Validation error",
            "details": exc.errors(),
        },
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(
    request: Request,
    exc: SQLAlchemyError,
) -> JSONResponse:
    """
    Handle SQLAlchemy database errors.

    Args:
        request: HTTP request
        exc: SQLAlchemyError instance

    Returns:
        JSON response with error message
    """
    logger.error(
        "Database error",
        exc_info=exc,
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "Database error occurred",
            "details": {} if settings.is_production else {"error": str(exc)},
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle all other unhandled exceptions.

    Args:
        request: HTTP request
        exc: Exception instance

    Returns:
        JSON response with error message
    """
    logger.error(
        "Unhandled exception",
        exc_info=exc,
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "Internal server error",
            "details": {} if settings.is_production else {"error": str(exc)},
        },
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": "1.0.0",
        "environment": settings.APP_ENV,
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> dict:
    """
    Root endpoint.

    Returns:
        Welcome message
    """
    return {
        "message": "Welcome to sMart Backend API",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }


# Include API routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
