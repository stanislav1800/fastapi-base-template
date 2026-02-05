from contextlib import asynccontextmanager

from src.main import app


@asynccontextmanager
async def override_dependencies(overrides: dict):
    app.dependency_overrides.update(overrides)
    yield
    app.dependency_overrides.clear()
