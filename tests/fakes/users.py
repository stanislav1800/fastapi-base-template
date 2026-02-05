from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.integration.base.unit_of_work import UnitOfWorkBase
from src.user.exceptions import UserNotFound
from src.user.models import User
from src.user.repository import UserRepository
from src.user.schemas import UserCreate, UserUpdate


class FakeUserRepository(UserRepository):
    def __init__(self):
        self._users = []

    async def add(self, user: UserCreate) -> User:
        user = User(id=self._get_new_user_id(), **user.model_dump(mode="json"))
        user.created_at = datetime.now(timezone.utc)
        self._users.append(user)
        return user

    async def get_by_pk(self, pk: UUID) -> User:
        for user in self._users:
            if user.id == pk:
                return user

        raise UserNotFound(detail=f"User with id {pk} not found")

    async def get_by_email(self, email: str) -> User:
        for user in self._users:
            if user.email == email:
                return user

        raise UserNotFound(detail=f"User with email {email} not found")

    async def update(self, user_data: UserUpdate) -> User:
        user = await self.get_by_pk(user_data.id)

        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        return user

    async def delete(self, pk: int) -> None:
        user = await self.get_by_pk(pk)
        self._users.remove(user)

    def _get_new_user_id(self) -> UUID:
        return uuid4()


class FakeUserUnitOfWork(UnitOfWorkBase):
    def __init__(self):
        self.users = FakeUserRepository()
        self.committed = False

    async def _commit(self):
        self.committed = True

    async def rollback(self):
        pass


class FakePasswordHasher:
    def __init__(self, expected_plain: str | None = None, expected_hashed: str | None = None):
        self.expected_plain = expected_plain
        self.expected_hashed = expected_hashed
        self.hash_calls: list[str] = []
        self.verify_called = False
        self.last_plain: str | None = None
        self.last_hashed: str | None = None

    def hash(self, password: str) -> str:
        self.hash_calls.append(password)
        return f"hashed-{password}"

    def verify(self, plain: str, hashed: str) -> bool:
        self.verify_called = True
        self.last_plain = plain
        self.last_hashed = hashed

        if self.expected_plain is None or self.expected_hashed is None:
            return hashed == f"hashed-{plain}"

        return plain == self.expected_plain and hashed == self.expected_hashed
