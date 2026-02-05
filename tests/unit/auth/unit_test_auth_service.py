import pytest
from pydantic import SecretStr
from unittest.mock import AsyncMock

from src.auth.exceptions import InvalidCredentials
from src.auth.service import authenticate
from src.user.schemas import UserCreate
from tests.fakes.users import FakePasswordHasher, FakeUserUnitOfWork


@pytest.mark.asyncio
async def test_authenticate_sets_tokens_on_success():
    uow = FakeUserUnitOfWork()
    user = await uow.users.add(
        UserCreate(
            email="user@example.com",
            hashed_password="hashed-secret",
            is_active=True,
        )
    )
    pwd_hasher = FakePasswordHasher(expected_plain="secret", expected_hashed="hashed-secret")
    auth = AsyncMock()

    await authenticate("user@example.com", SecretStr("secret"), pwd_hasher, uow, auth)

    assert pwd_hasher.verify_called is True
    assert pwd_hasher.last_plain == "secret"
    assert pwd_hasher.last_hashed == "hashed-secret"
    auth.set_tokens.assert_awaited_once_with(user)


@pytest.mark.asyncio
async def test_authenticate_raises_on_invalid_credentials():
    uow = FakeUserUnitOfWork()
    await uow.users.add(
        UserCreate(
            email="user@example.com",
            hashed_password="hashed-secret",
            is_active=True,
        )
    )
    pwd_hasher = FakePasswordHasher(expected_plain="secret", expected_hashed="hashed-secret")
    auth = AsyncMock()

    with pytest.raises(InvalidCredentials):
        await authenticate("user@example.com", SecretStr("wrong"), pwd_hasher, uow, auth)

    auth.set_tokens.assert_not_awaited()
