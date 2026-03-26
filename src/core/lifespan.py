import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.infrastructure.aiohttp_client import close_aiohttp_client, init_aiohttp_client
from src.core.infrastructure.redis_client import close_redis, init_redis


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application")
    await init_redis()
    # await init_aiohttp_client()
    yield
    logger.info("Shutting down application")
    await close_redis()
    # await close_aiohttp_client()
