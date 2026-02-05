import logging
from typing import AsyncIterator

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.core.config import settings
import src.core.middleware as core_middleware
import src.database.engine as db_engine
import src.database.session as db_session
from src.database.base import Base
import src.user.models  # noqa: F401  # ensure model metadata is registered


logger = logging.getLogger(__name__)




async def _ensure_test_db_exists() -> None:
    admin_url = (
        f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/postgres"
    )
    admin_engine = create_async_engine(admin_url, poolclass=NullPool)
    try:
        async with admin_engine.connect() as conn:
            result = await conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": settings.DB_NAME},
            )
            exists = result.scalar() is not None

        if not exists:
            async with admin_engine.connect() as conn:
                autocommit_conn = await conn.execution_options(isolation_level="AUTOCOMMIT")
                await autocommit_conn.execute(text(f'CREATE DATABASE "{settings.DB_NAME}"'))
    except SQLAlchemyError as exc:
        pytest.skip(f"Cannot create test database automatically: {exc}")
    finally:
        await admin_engine.dispose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def configure_test_engine() -> AsyncIterator[None]:
    original_db_name = settings.DB_NAME

    if not settings.DB_NAME.lower().endswith("_test"):
        settings.DB_NAME += "_test"

    if "test" not in settings.DB_NAME.lower():
        pytest.skip("DB_NAME must contain 'test' for safety reasons")

    await _ensure_test_db_exists()

    test_engine = create_async_engine(settings.get_db_url(), poolclass=NullPool)
    test_session_maker = async_sessionmaker(test_engine, expire_on_commit=False)

    db_engine.engine = test_engine
    db_engine.async_session_maker = test_session_maker
    db_session.async_session_maker = test_session_maker
    core_middleware.async_session_maker = test_session_maker

    yield

    # ───────────────────────────────────────────────
    # Закрываем все соединения к тестовой базе
    await test_engine.dispose()

    admin_url = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/postgres"
    admin_engine = create_async_engine(admin_url, poolclass=NullPool)

    try:
        conn = await admin_engine.connect()
        try:
            # Разделяем цепочку на две строки — убирает любые неоднозначности
            opts_conn = await conn.execution_options(isolation_level="AUTOCOMMIT")
            await opts_conn.execute(
                text(f'DROP DATABASE IF EXISTS "{settings.DB_NAME}"')
            )
            logger.info(f"→ Test database dropped successfully: {settings.DB_NAME}")
        finally:
            await conn.close()
    except Exception as e:
        logger.info(f"→ Could not drop test database {settings.DB_NAME}: {e}")
    finally:
        await admin_engine.dispose()

    # Опционально: вернуть оригинальное имя (редко нужно)
    # settings.DB_NAME = original_db_name


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database(configure_test_engine) -> AsyncIterator[None]:
    async with db_engine.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with db_engine.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(autouse=True)
async def clean_database() -> AsyncIterator[None]:
    async with db_engine.async_session_maker() as session:
        await session.execute(text('DELETE FROM "user"'))
        await session.commit()
    yield


@pytest_asyncio.fixture(autouse=True)
async def clean_redis() -> AsyncIterator[None]:
    # Используем session-scoped redis из root tests/conftest.py
    from src.core.infrastructure.redis_client import get_redis as _get_redis

    redis = _get_redis()

    await redis.flushdb()
    try:
        yield
    finally:
        await redis.flushdb()
