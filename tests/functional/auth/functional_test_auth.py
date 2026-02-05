import httpx
import pytest

from src.auth.dependencies import get_token_auth
from src.user.dependencies import get_user_uow
from src.user.schemas import UserCreate
from tests.utils import override_dependencies

user_create_data = UserCreate(
    email="user@example.com",
    hashed_password="securepassword!1_hashed",
    is_active=True,
    is_superuser=False,
    is_verified=True,
)


@pytest.mark.asyncio
async def test_login_success(set_fake_check_password, client: httpx.AsyncClient, mock_auth, fake_user_uow):
    set_fake_check_password(True)
    async with override_dependencies({get_token_auth: lambda: mock_auth, get_user_uow: lambda: fake_user_uow}):
        await fake_user_uow.users.add(user_create_data)

        response = await client.post("/api/auth/login", json={"email": "user@example.com", "password": "12345678"})
        assert response.status_code == 200
        assert response.json() == {"detail": "Tokens set"}
        mock_auth.set_tokens.assert_awaited_once()


@pytest.mark.asyncio
async def test_refresh_access_token(client: httpx.AsyncClient, mock_auth):
    async with override_dependencies({get_token_auth: lambda: mock_auth}):
        response = await client.post("/api/auth/refresh")
        assert response.status_code == 200
        assert response.json() == {"detail": "Token refreshed"}
        mock_auth.refresh_access_token.assert_awaited_once()


@pytest.mark.asyncio
async def test_logout(client: httpx.AsyncClient, mock_auth):
    async with override_dependencies({get_token_auth: lambda: mock_auth}):
        response = await client.post("/api/auth/logout")
        assert response.status_code == 200
        assert response.json() == {"detail": "Tokens deleted"}
        mock_auth.unset_tokens.assert_awaited_once()
