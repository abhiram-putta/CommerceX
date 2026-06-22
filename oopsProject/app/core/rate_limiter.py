"""
Rate limiting middleware using Redis.
Implements token bucket algorithm for API rate limiting.
"""
import time
from typing import Optional

from fastapi import Request
from redis import asyncio as aioredis

from app.config.settings import get_settings
from app.core.exceptions import RateLimitError
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class RateLimiter:
    """
    Rate limiter using Redis.

    Implements sliding window rate limiting to control API request rates.
    """

    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize rate limiter.

        Args:
            redis_url: Redis connection URL (uses settings if not provided)
        """
        self.redis_url = redis_url or settings.REDIS_URL
        self.redis_client: Optional[aioredis.Redis] = None
        self.rate_limit = settings.RATE_LIMIT_PER_MINUTE
        self.window_seconds = 60

    async def connect(self):
        """Connect to Redis."""
        if not self.redis_client:
            try:
                self.redis_client = await aioredis.from_url(
                    self.redis_url,
                    encoding="utf-8",
                    decode_responses=True
                )
                logger.info("Rate limiter connected to Redis")
            except Exception as e:
                logger.error(f"Failed to connect to Redis for rate limiting: {e}")
                self.redis_client = None

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None

    def _get_client_identifier(self, request: Request) -> str:
        """
        Get unique identifier for the client.

        Uses user ID if authenticated, otherwise uses IP address.

        Args:
            request: FastAPI request object

        Returns:
            Client identifier string
        """
        # Try to get user from request state
        user = getattr(request.state, "user", None)
        if user and hasattr(user, "id"):
            return f"user:{user.id}"

        # Fall back to IP address
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            ip = forwarded.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"

        return f"ip:{ip}"

    async def check_rate_limit(
        self,
        request: Request,
        limit: Optional[int] = None,
        window_seconds: Optional[int] = None
    ) -> bool:
        """
        Check if request is within rate limit.

        Args:
            request: FastAPI request object
            limit: Custom rate limit (uses default if not provided)
            window_seconds: Custom window in seconds (uses default if not provided)

        Returns:
            True if within limit, False otherwise

        Raises:
            RateLimitError: If rate limit is exceeded
        """
        # If Redis is not available, allow the request
        if not self.redis_client:
            logger.warning("Redis not available, rate limiting disabled")
            return True

        limit = limit or self.rate_limit
        window_seconds = window_seconds or self.window_seconds

        client_id = self._get_client_identifier(request)
        key = f"rate_limit:{client_id}"
        current_time = int(time.time())
        window_start = current_time - window_seconds

        try:
            # Use Redis sorted set to track requests in sliding window
            pipe = self.redis_client.pipeline()

            # Remove old entries outside the window
            pipe.zremrangebyscore(key, 0, window_start)

            # Count requests in current window
            pipe.zcard(key)

            # Add current request
            pipe.zadd(key, {str(current_time): current_time})

            # Set expiration on the key
            pipe.expire(key, window_seconds)

            results = await pipe.execute()
            request_count = results[1]  # Result from zcard

            if request_count >= limit:
                logger.warning(
                    f"Rate limit exceeded for {client_id}: "
                    f"{request_count}/{limit} requests in {window_seconds}s"
                )
                raise RateLimitError(
                    f"Rate limit exceeded. Maximum {limit} requests per {window_seconds} seconds."
                )

            return True

        except RateLimitError:
            raise
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # On error, allow the request through
            return True

    async def get_rate_limit_status(
        self,
        request: Request,
        window_seconds: Optional[int] = None
    ) -> dict:
        """
        Get current rate limit status for client.

        Args:
            request: FastAPI request object
            window_seconds: Custom window in seconds

        Returns:
            Dictionary with rate limit status
        """
        if not self.redis_client:
            return {
                "limit": self.rate_limit,
                "remaining": self.rate_limit,
                "reset": int(time.time()) + self.window_seconds
            }

        window_seconds = window_seconds or self.window_seconds
        client_id = self._get_client_identifier(request)
        key = f"rate_limit:{client_id}"
        current_time = int(time.time())
        window_start = current_time - window_seconds

        try:
            # Remove old entries and count remaining
            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            results = await pipe.execute()
            request_count = results[1]

            remaining = max(0, self.rate_limit - request_count)
            reset_time = current_time + window_seconds

            return {
                "limit": self.rate_limit,
                "remaining": remaining,
                "reset": reset_time,
                "current_requests": request_count
            }

        except Exception as e:
            logger.error(f"Error getting rate limit status: {e}")
            return {
                "limit": self.rate_limit,
                "remaining": self.rate_limit,
                "reset": current_time + window_seconds
            }


# Global rate limiter instance
rate_limiter = RateLimiter()
