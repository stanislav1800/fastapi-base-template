from redis.asyncio.client import Redis
import logging

from src.auth.infrastructure.token_storage.base import TokenStorageBase
from src.core.infrastructure.redis_client import get_redis
from src.core.security.jwt import TokenData
from src.integration.utils.datetimes import get_timezone_now


logger = logging.getLogger(__name__)

class RedisTokenStorage(TokenStorageBase):
    def __init__(self, client: Redis | None = None):
        # Клиент можно передать извне (DI). Если не передан — используем глобальный.
        self._client = client or get_redis()

    async def store_token(self, token_data: TokenData) -> None:
        ttl = token_data.exp - int(get_timezone_now().timestamp())

        await self._client.setex(f"tokens:{token_data.jti}", ttl, str(token_data.user_id))
        await self._client.sadd(f"user_tokens:{token_data.user_id}", token_data.jti)

    async def revoke_tokens_by_jti(self, jti: str, user_id: str):
        await self._client.delete(f"tokens:{jti}")
        await self._client.srem(f"user_tokens:{user_id}", jti)

    async def revoke_tokens_by_user(self, user_id: str) -> None:
        token_keys = await self._client.smembers(f"user_tokens:{user_id}")
        for jti in token_keys:
            jti_str = jti.decode() if isinstance(jti, bytes) else jti
            await self._client.delete(f"tokens:{jti_str}")
        await self._client.delete(f"user_tokens:{user_id}")

    async def is_token_active(self, jti: str) -> bool:
        return await self._client.exists(f"tokens:{jti}") == 1
