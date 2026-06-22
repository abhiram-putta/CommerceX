"""
Redis caching utilities for performance optimization.
"""
import json
from typing import Any, Optional, Union
from datetime import timedelta
import redis.asyncio as redis
from functools import wraps

from app.config.settings import get_settings


class CacheManager:
    """
    Redis cache manager for application-wide caching.
    """

    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.default_ttl = 300  # 5 minutes default

    async def connect(self):
        """Connect to Redis."""
        if not self.redis_client:
            self.redis_client = await redis.from_url(
                get_settings().REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
            )

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            self.redis_client = None

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self.redis_client:
            await self.connect()

        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error for key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (default: 300)

        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            await self.connect()

        try:
            ttl = ttl or self.default_ttl
            serialized = json.dumps(value, default=str)
            await self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            print(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if deleted, False otherwise
        """
        if not self.redis_client:
            await self.connect()

        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error for key {key}: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern.

        Args:
            pattern: Redis key pattern (e.g., "products:*")

        Returns:
            Number of keys deleted
        """
        if not self.redis_client:
            await self.connect()

        try:
            keys = []
            async for key in self.redis_client.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Cache delete pattern error for {pattern}: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key to check

        Returns:
            True if exists, False otherwise
        """
        if not self.redis_client:
            await self.connect()

        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            print(f"Cache exists error for key {key}: {e}")
            return False

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment counter in cache.

        Args:
            key: Cache key
            amount: Amount to increment by

        Returns:
            New value or None on error
        """
        if not self.redis_client:
            await self.connect()

        try:
            return await self.redis_client.incrby(key, amount)
        except Exception as e:
            print(f"Cache increment error for key {key}: {e}")
            return None

    async def set_hash(self, key: str, mapping: dict, ttl: Optional[int] = None):
        """
        Set hash in cache.

        Args:
            key: Cache key
            mapping: Dictionary to store as hash
            ttl: Time to live in seconds
        """
        if not self.redis_client:
            await self.connect()

        try:
            # Serialize complex values
            serialized_mapping = {
                k: json.dumps(v, default=str) if not isinstance(v, (str, int, float)) else v
                for k, v in mapping.items()
            }
            await self.redis_client.hset(key, mapping=serialized_mapping)
            if ttl:
                await self.redis_client.expire(key, ttl)
        except Exception as e:
            print(f"Cache set_hash error for key {key}: {e}")

    async def get_hash(self, key: str) -> Optional[dict]:
        """
        Get hash from cache.

        Args:
            key: Cache key

        Returns:
            Dictionary or None if not found
        """
        if not self.redis_client:
            await self.connect()

        try:
            data = await self.redis_client.hgetall(key)
            if data:
                # Deserialize complex values
                return {
                    k: json.loads(v) if v.startswith('{') or v.startswith('[') else v
                    for k, v in data.items()
                }
            return None
        except Exception as e:
            print(f"Cache get_hash error for key {key}: {e}")
            return None

    async def clear_all(self) -> bool:
        """
        Clear all cache (use with caution!).

        Returns:
            True if successful
        """
        if not self.redis_client:
            await self.connect()

        try:
            await self.redis_client.flushdb()
            return True
        except Exception as e:
            print(f"Cache clear_all error: {e}")
            return False


# Global cache manager instance
cache_manager = CacheManager()


def cache_key(*args, prefix: str = "") -> str:
    """
    Generate cache key from arguments.

    Args:
        *args: Key components
        prefix: Optional prefix

    Returns:
        Generated cache key
    """
    parts = [str(arg) for arg in args if arg is not None]
    key = ":".join(parts)
    if prefix:
        key = f"{prefix}:{key}"
    return key


def cached(
    ttl: int = 300,
    key_prefix: str = "",
    key_builder: Optional[callable] = None,
):
    """
    Decorator to cache function results.

    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
        key_builder: Custom function to build cache key from args

    Example:
        @cached(ttl=600, key_prefix="product")
        async def get_product(product_id: UUID):
            # Function body
            pass
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            if key_builder:
                cache_key_str = key_builder(*args, **kwargs)
            else:
                # Default: use function name and args
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key_str = cache_key(*key_parts, prefix=key_prefix)

            # Try to get from cache
            cached_value = await cache_manager.get(cache_key_str)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            if result is not None:
                await cache_manager.set(cache_key_str, result, ttl=ttl)

            return result

        return wrapper
    return decorator


# Cache key patterns for invalidation
class CacheKeys:
    """Cache key patterns for different entities."""

    # Products
    PRODUCT = "product:{id}"
    PRODUCTS_LIST = "products:list:{filters}"
    PRODUCT_SEARCH = "products:search:{query}"
    PRODUCT_CATEGORY = "products:category:{category_id}"

    # Categories
    CATEGORY = "category:{id}"
    CATEGORIES_LIST = "categories:list"
    CATEGORY_TREE = "categories:tree"

    # Cart
    CART = "cart:{user_id}"
    CART_COUNT = "cart:count:{user_id}"

    # Wishlist
    WISHLIST = "wishlist:{user_id}"
    WISHLIST_COUNT = "wishlist:count:{user_id}"

    # User
    USER = "user:{id}"
    USER_PROFILE = "user:profile:{id}"

    # Analytics
    ANALYTICS_SALES = "analytics:sales:{period}"
    ANALYTICS_REVENUE = "analytics:revenue:{period}"

    # Recommendations
    RECOMMENDATIONS = "recommendations:{user_id}"
    TRENDING = "trending:products"
