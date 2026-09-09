from redis.asyncio import Redis
from core.config import settings

_redis_client = None

async def get_redis_client() -> Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(settings.REDIS_URL, max_connections=10, \
                                       socket_timeout=2, socket_connect_timeout=2, \
                                       retry_on_timeout=True, decode_responses=True)
    return _redis_client

async def close_redis_client():
    global _redis_client 
    if _redis_client is not None:
        try:
            await _redis_client.close()
        except Exception as e:
            print(f'Ошибка при закрытии Redis: {e}')
        finally:
            _redis_client = None