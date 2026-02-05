import httpx
from uuid import UUID, uuid4

from src.core.security.jwt import JWTProvider


async def create_user_via_api(client: httpx.AsyncClient, email: str = "user@example.com") -> dict:
    response = await client.get(f"/api/users/{uuid4()}")
    assert response.status_code == 404

    response = await client.post(
        url="/api/users",
        json={
            "email": email,
            "password": "12345",
        },
    )
    assert response.status_code == 200
    return response.json()


def create_access_token(user_id: UUID) -> str:
    token_provider = JWTProvider()
    data = {
        "user_id": str(user_id),
    }
    access_token = token_provider.create_access_token(data)
    return access_token
