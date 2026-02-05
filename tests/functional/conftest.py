from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core.security.security import PasswordHasher
from src.main import app
from src.user.dependencies import get_user_uow
from tests.fakes.users import FakeUserUnitOfWork


@pytest.fixture()
def mock_auth():
    mock_auth = MagicMock()
    mock_auth.set_tokens = AsyncMock()
    mock_auth.unset_tokens = AsyncMock()
    mock_auth.refresh_access_token = AsyncMock()
    mock_auth.token_storage = MagicMock()
    mock_auth.token_storage.revoke_tokens_by_user = AsyncMock()
    return mock_auth


@pytest.fixture
def override_user_uow():
    uow = FakeUserUnitOfWork()
    app.dependency_overrides[get_user_uow] = lambda: uow
    yield uow
    app.dependency_overrides = {}


@pytest.fixture
def set_fake_check_password(monkeypatch):
    def _patch(return_value: bool):
        monkeypatch.setattr(PasswordHasher, "verify", lambda self, password, hashed: return_value)

    return _patch
