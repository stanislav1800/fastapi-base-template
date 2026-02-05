from datetime import datetime, timezone
from uuid import uuid4

import httpx
import pytest

from src.user.dependencies import get_user_uow
from src.user.router import get_current_active_user
from src.core.security.permissions import require_self_or_superuser
from src.user.schemas import User
from tests.functional.users.utils import create_user_via_api
from tests.utils import override_dependencies


def _fake_current_user() -> User:
    return User(
        id=uuid4(),
        email="test@example.com",
        hashed_password="hashed",
        is_active=True,
        is_superuser=False,
        is_verified=True,
        created_at=datetime.now(timezone.utc),
    )


@pytest.mark.asyncio
async def test_register(client: httpx.AsyncClient, fake_user_uow):
    async with override_dependencies({get_user_uow: lambda: fake_user_uow}):
        new_user_data = await create_user_via_api(client, "user@example.com")
        assert new_user_data["email"] == "user@example.com"


@pytest.mark.asyncio
async def test_get_profile(client: httpx.AsyncClient, fake_user_uow):
    async with override_dependencies(
        {
            get_user_uow: lambda: fake_user_uow,
            get_current_active_user: _fake_current_user,
        }
    ):
        new_user_data = await create_user_via_api(client, "user@example.com")
        response = await client.get(f"/api/users/{new_user_data['id']}")
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["email"] == new_user_data["email"]


@pytest.mark.asyncio
async def test_delete_user(client: httpx.AsyncClient, fake_user_uow):
    async with override_dependencies(
        {
            get_user_uow: lambda: fake_user_uow,
            require_self_or_superuser: lambda: None,
        }
    ):
        new_user_data = await create_user_via_api(client, "user@example.com")
        response = await client.delete(f"/api/users/{new_user_data['id']}")
        assert response.status_code == 204


@pytest.mark.asyncio
async def test_update_user(client: httpx.AsyncClient, fake_user_uow):
    async with override_dependencies(
        {
            get_user_uow: lambda: fake_user_uow,
            require_self_or_superuser: lambda: None,
        }
    ):
        new_user_data = await create_user_via_api(client, "user@example.com")
        response = await client.patch(
            f"/api/users/{new_user_data['id']}",
            json={
                "email": "update_user@example.com",
            },
        )
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["email"] == "update_user@example.com"
