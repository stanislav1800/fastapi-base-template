from typing import AsyncIterator

import httpx
import pytest
import pytest_asyncio

from tests.fakes.users import FakeUserUnitOfWork
import asyncio

from src.core.infrastructure.redis_client import init_redis, close_redis


@pytest_asyncio.fixture()
async def client() -> AsyncIterator[httpx.AsyncClient]:
    from src.main import app

    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        yield client


@pytest.fixture
def fake_user_uow():
    return FakeUserUnitOfWork()


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    prev = asyncio.get_event_loop_policy().get_event_loop()
    asyncio.set_event_loop(loop)
    try:
        yield loop
    finally:
        try:
            asyncio.set_event_loop(prev)
        except Exception:
            pass
        loop.close()


@pytest_asyncio.fixture(autouse=True)
async def redis_session():
    """Инициализирует Redis для каждого теста — гарантирует совпадение event loop."""
    await init_redis()
    try:
        yield
    finally:
        await close_redis()
