import json
from typing import Any, Awaitable, Callable
from redis.exceptions import RedisError
from cache.redis_client import get_redis_client

async def get_cache(key: str) -> Any | None:
    """Читает значение из Redis и десериализует JSON."""
    if not key:
        return None
    try:
        client = await get_redis_client()
        result = await client.get(key)
        if result is None:
            return None
        return json.loads(result)
    except RedisError as e:
        """Место для логирования."""
        return None
    except json.JSONDecodeError as e:
        """Место для логирования."""
        return None

async def set_cache(key: str, value: Any, ttl: int) -> None:
    """Сохраняет значение в Redis с TTL (в секундах)."""
    if not key or ttl <= 0:
        return
    try:
        serialized = json.dumps(value, default=str, ensure_ascii=False)
        client = await get_redis_client()
        await client.set(key, serialized, ex=ttl)
    except RedisError as e:
        """Место для логирования."""

async def delete_cache(key: str) -> None:
    """Удаляет один ключ из Redis. Ошибки логируются, но не падают."""
    if not key:
        return
    try:
        client = await get_redis_client()
        await client.delete(key)
    except RedisError as e:
        """Место для логирования."""

async def delete_cache_by_pattern(pattern: str) -> int:
    """Удаляет все ключи, подходящие под glob-паттерн, через SCAN."""
    if not pattern:
        return 0
    deleted = 0
    try:
        client = await get_redis_client()
        async for key in client.scan_iter(match=pattern, count=100):
            await client.delete(key)
            deleted += 1
    except RedisError as e:
        """Место для логирования."""
    return deleted

async def get_or_set(key: str, factory: Callable[[], Awaitable[Any]], ttl: int,) -> Any:
    """Cache-aside: возвращает из кэша или вычисляет и кэширует."""
    cached = await get_cache(key)
    if cached is not None:
        return cached
    value = await factory()
    await set_cache(key, value, ttl)
    return value