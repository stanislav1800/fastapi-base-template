from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.integration.base.unit_of_work import UnitOfWorkBase
from src.user.repository import UserRepository


class UserUnitOfWork(UnitOfWorkBase):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def __aenter__(self):
        self._session = self._session_factory()
        self.users = UserRepository(self._session)
        return self

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self._session.close()

    async def _commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()
