from redis.asyncio import Redis
from core.config import settings

_redis_client: Redis | None = None

async def get_redis_client() -> Redis:
    """Возвращает singleton-клиент Redis (ленивая инициализация)."""
    global _redis_client
    if _redis_client is None:
        _redis_client = Redis.from_url(
            settings.REDIS_URL,
            max_connections=10,
            socket_timeout=2,
            socket_connect_timeout=2,
            decode_responses=True,
        )
    return _redis_client


async def close_redis_client() -> None:
    """Закрывает соединение с Redis. Вызывается при shutdown приложения."""
    global _redis_client
    if _redis_client is not None:
        try:
            await _redis_client.aclose()
        except Exception as e:
            """Место для логирования."""
        finally:
            _redis_client = None


async def ping_redis() -> bool:
    """Проверяет доступность Redis. Используется в /health."""
    try:
        client = await get_redis_client()
        return bool(await client.ping())
    except Exception as e:
        """Место для логирования."""
        return False


async def redis_health() -> dict:
    """Возвращает словарь со статусом Redis для healthcheck-эндпоинта."""
    ok = await ping_redis()
    return {'redis': 'ok' if ok else 'unavailable'}