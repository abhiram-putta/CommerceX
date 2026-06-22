"""
Redis client configuration for caching and session management.
"""
from typing import Optional, Any
import json
from redis import asyncio as aioredis
from redis.asyncio import Redis

from app.config.settings import get_settings
from app.utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


class RedisClient:
    """
    Redis client wrapper with caching utilities.
    Provides async methods for Redis operations.
    """

    def __init__(self) -> None:
        """Initialize Redis client."""
        self._redis: Optional[Redis] = None

    async def connect(self) -> None:
        """Establish connection to Redis."""
        try:
            self._redis = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=50,
            )
            await self._redis.ping()
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self) -> None:
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            logger.info("Redis connection closed")

    async def get(self, key: str) -> Optional[str]:
        """
        Get value from Redis.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self._redis:
            logger.warning("Redis client not initialized")
            return None

        try:
            return await self._redis.get(key)
        except Exception as e:
            logger.error(f"Error getting key {key} from Redis: {e}")
            return None

    async def set(
        self,
        key: str,
        value: str,
        expire: Optional[int] = None,
    ) -> bool:
        """
        Set value in Redis with optional expiration.

        Args:
            key: Cache key
            value: Value to cache
            expire: Expiration time in seconds (default: REDIS_CACHE_TTL)

        Returns:
            True if successful, False otherwise
        """
        if not self._redis:
            logger.warning("Redis client not initialized")
            return False

        try:
            expire = expire or settings.REDIS_CACHE_TTL
            await self._redis.set(key, value, ex=expire)
            return True
        except Exception as e:
            logger.error(f"Error setting key {key} in Redis: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete key from Redis.

        Args:
            key: Cache key to delete

        Returns:
            True if successful, False otherwise
        """
        if not self._redis:
            logger.warning("Redis client not initialized")
            return False

        try:
            await self._redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Error deleting key {key} from Redis: {e}")
            return False

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in Redis.

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        if not self._redis:
            return False

        try:
            return bool(await self._redis.exists(key))
        except Exception as e:
            logger.error(f"Error checking existence of key {key}: {e}")
            return False

    async def get_json(self, key: str) -> Optional[Any]:
        """
        Get JSON value from Redis.

        Args:
            key: Cache key

        Returns:
            Deserialized JSON value or None
        """
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON for key {key}: {e}")
        return None

    async def set_json(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None,
    ) -> bool:
        """
        Set JSON value in Redis.

        Args:
            key: Cache key
            value: Value to serialize and cache
            expire: Expiration time in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            json_value = json.dumps(value)
            return await self.set(key, json_value, expire)
        except (TypeError, ValueError) as e:
            logger.error(f"Error encoding JSON for key {key}: {e}")
            return False

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment value in Redis.

        Args:
            key: Cache key
            amount: Amount to increment by

        Returns:
            New value after increment or None
        """
        if not self._redis:
            return None

        try:
            return await self._redis.incrby(key, amount)
        except Exception as e:
            logger.error(f"Error incrementing key {key}: {e}")
            return None

    async def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiration time for a key.

        Args:
            key: Cache key
            seconds: Expiration time in seconds

        Returns:
            True if successful, False otherwise
        """
        if not self._redis:
            return False

        try:
            return bool(await self._redis.expire(key, seconds))
        except Exception as e:
            logger.error(f"Error setting expiration for key {key}: {e}")
            return False


# Global Redis client instance
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """
    Dependency function to get Redis client.

    Returns:
        RedisClient instance
    """
    return redis_client
