from cache.redis_client import get_redis_client
import json 
from redis.exceptions import RedisError
import redis
from typing import Any, Callable, Awaitable
from cache.cache_keys import TTL

async def get_cache(key: str) -> Any | None:
    """"""
    try:
        if not key:
            return None
        client = await get_redis_client()
        result = await client.get(key)
        if result is None:
            return None
        else:
            return json.loads(result)
    except RedisError:
        return None
    

async def set_cache(key: str, value: Any, ttl: int) -> None:
    """"""
    try:
        if not key or ttl <= 0:
            return None
        serialized = json.dumps(value, default=str, ensure_ascii=False)
        client = await get_redis_client()
        await client.set(key, serialized, ex=ttl) 
    except RedisError:
        return None

async def delete_cache(key: str) -> None:
    """"""
    try:
        if not key:
            return None
        client = await get_redis_client()
        await client.delete(key)
    except RedisError:
        return None

async def delete_cache_by_pattern(pattern: str) -> int:
    """"""
    client = await get_redis_client()
    deleted = 0
    async for key in client.scan_iter(match=pattern, count=100):
        await client.delete(key)
        delete += 1
    return deleted

async def get_or_set(key: str, factory: Callable[[], Awaitable[Any]], ttl: int) -> Any: 
    """"""
    cached = await get_cache(key)
    if cached is not None:
        return cached
    value = await factory()
    await set_cache(key, value, ttl)
    return value