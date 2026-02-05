import httpx

from src.core.config import settings


async def register_user(client: httpx.AsyncClient, email: str, password: str) -> str:
    response = await client.post(
        "/api/users",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()["id"]


async def login_user(client: httpx.AsyncClient, email: str, password: str) -> str:
    response = await client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    assert response.json() == {"detail": "Tokens set"}

    access_header_name = settings.access_token_header_name
    access_header_value = response.headers.get(access_header_name)
    assert access_header_value, f"Missing access token header: {access_header_name}"
    return extract_bearer_token(access_header_value)


def extract_bearer_token(header_value: str) -> str:
    parts = header_value.split(" ")
    if len(parts) == 2:
        return parts[1]
    return header_value
