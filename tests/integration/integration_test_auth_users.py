import httpx
import pytest

from src.core.config import settings
from tests.integration.utils import extract_bearer_token, login_user, register_user


@pytest.mark.asyncio
async def test_register_login_profile_update_delete_flow(client: httpx.AsyncClient):
    email = "user@example.com"
    password = "super-secret"

    user_id = await register_user(client, email, password)
    access_token = await login_user(client, email, password)

    access_header_name = settings.access_token_header_name
    auth_headers = {access_header_name: f"{settings.jwt_header_type} {access_token}"}

    response = await client.get(f"/api/users/{user_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == email

    response = await client.patch(
        f"/api/users/{user_id}",
        headers=auth_headers,
        json={"email": "updated@example.com", "is_active": False},
    )
    assert response.status_code == 200
    assert response.json()["email"] == "updated@example.com"
    assert response.json()["is_active"] is False

    response = await client.delete(f"/api/users/{user_id}", headers=auth_headers)
    assert response.status_code == 204

    response = await client.get(f"/api/users/{user_id}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_refresh_and_logout_flow(client: httpx.AsyncClient):
    email = "refresh@example.com"
    password = "super-secret"

    await register_user(client, email, password)

    original_refresh_transport = settings.refresh_token_transport
    try:
        settings.refresh_token_transport = "header"

        response = await client.post(
            "/api/auth/login",
            json={"email": email, "password": password},
        )
        assert response.status_code == 200

        access_header_name = settings.access_token_header_name
        refresh_header_name = settings.refresh_token_header_name

        access_header_value = response.headers.get(access_header_name)
        refresh_header_value = response.headers.get(refresh_header_name)
        assert access_header_value, f"Missing access token header: {access_header_name}"
        assert refresh_header_value, f"Missing refresh token header: {refresh_header_name}"

        access_token = extract_bearer_token(access_header_value)
        refresh_token = extract_bearer_token(refresh_header_value)

        refresh_headers = {refresh_header_name: f"{settings.jwt_header_type} {refresh_token}"}
        response = await client.post("/api/auth/refresh", headers=refresh_headers)
        assert response.status_code == 200
        assert response.json() == {"detail": "Token refreshed"}

        auth_headers = {access_header_name: f"{settings.jwt_header_type} {access_token}"}
        response = await client.post("/api/auth/logout", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == {"detail": "Tokens deleted"}
    finally:
        settings.refresh_token_transport = original_refresh_transport
