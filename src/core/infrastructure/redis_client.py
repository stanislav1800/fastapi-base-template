import asyncio
import logging
import redis.asyncio as redis

from src.core.config import settings

_redis: redis.Redis | None = None
logger = logging.getLogger(__name__)


async def init_redis() -> redis.Redis | None:
    """Инициализировать клиент redis и вернуть его."""
    global _redis
    if _redis is not None:
        return _redis

    try:
        running_loop = asyncio.get_running_loop()
    except RuntimeError:
        running_loop = None
    logger.debug("init_redis running on loop: %s", running_loop)

    _redis = redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_timeout=5,
        socket_connect_timeout=5,
        max_connections=20,
    )
    await _redis.ping()
    logger.info("Redis initialized", extra={"redis_url": settings.redis_url})
    logger.debug("redis client created: %r", _redis)
    return _redis


async def close_redis() -> None:
    """Закрыть подключение к Redis. Бережно игнорируем ошибки, связанные с уже закрытым loop."""
    global _redis
    if _redis:
        try:
            await _redis.aclose()
        except RuntimeError:
            # Иногда loop уже закрыт — попытаемся аккуратно вызвать асинхронное отключение пула
            try:
                await _redis.connection_pool.disconnect()
            except Exception:
                pass
        except Exception:
            # Не даём исключению прерывать teardown тестов
            try:
                await _redis.connection_pool.disconnect()
            except Exception:
                pass
        finally:
            _redis = None
            logger.info("Redis connection closed")


def get_redis() -> redis.Redis:
    """Вернёт глобальный клиент Redis. Если клиент ещё не инициализирован,
    создаст экземпляр клиента лениво (без выполнения network ping). Это
    позволяет синхронно запрашивать клиент (например в __init__ классов),
    а инициализация/проверка доступности redis всё ещё может выполняться
    асинхронно через `init_redis()` в тестах/стартапе приложения.
    """
    global _redis
    if _redis is None:
        raise RuntimeError("Redis not initialized")
    return _redis
