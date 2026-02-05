import pytest

from src.user.exceptions import UserNotFound
from src.user.schemas import UserCreateBody, UserUpdateBody
from src.user.service import delete_user, get_user_profile, register_user, update_user
from tests.fakes.users import FakePasswordHasher, FakeUserUnitOfWork


@pytest.mark.asyncio
async def test_register_user_hashes_password_and_commits():
    uow = FakeUserUnitOfWork()
    pwd_hasher = FakePasswordHasher()
    user_data = UserCreateBody(
        email="user@example.com",
        password="secret",
        is_active=True,
        is_superuser=False,
        is_verified=True,
    )

    user = await register_user(user_data, pwd_hasher, uow)

    assert user.email == "user@example.com"
    assert user.hashed_password == "hashed-secret"
    assert uow.committed is True
    assert pwd_hasher.hash_calls == ["secret"]


@pytest.mark.asyncio
async def test_get_user_profile_returns_user():
    uow = FakeUserUnitOfWork()
    created = await register_user(
        UserCreateBody(
            email="user@example.com",
            password="secret",
            is_active=True,
            is_superuser=False,
            is_verified=False,
        ),
        FakePasswordHasher(),
        uow,
    )

    found = await get_user_profile(created.id, uow)

    assert found.id == created.id
    assert found.email == created.email


@pytest.mark.asyncio
async def test_update_user_changes_fields_and_commits():
    uow = FakeUserUnitOfWork()
    created = await register_user(
        UserCreateBody(
            email="user@example.com",
            password="secret",
            is_active=True,
            is_superuser=False,
            is_verified=False,
        ),
        FakePasswordHasher(),
        uow,
    )
    uow.committed = False

    updated = await update_user(
        created.id,
        UserUpdateBody(email="updated@example.com", is_active=False),
        uow,
    )

    assert updated.id == created.id
    assert updated.email == "updated@example.com"
    assert updated.is_active is False
    assert uow.committed is True


@pytest.mark.asyncio
async def test_delete_user_removes_user_and_commits():
    uow = FakeUserUnitOfWork()
    created = await register_user(
        UserCreateBody(
            email="user@example.com",
            password="secret",
            is_active=True,
            is_superuser=False,
            is_verified=False,
        ),
        FakePasswordHasher(),
        uow,
    )
    uow.committed = False

    await delete_user(created.id, uow)

    assert uow.committed is True
    with pytest.raises(UserNotFound):
        await get_user_profile(created.id, uow)
