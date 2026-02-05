from sqlalchemy.ext.asyncio import AsyncSession

from src.database.engine import async_session_maker
from src.integration.base.unit_of_work import UnitOfWorkBase
from src.user.repository import UserRepository


class UserUnitOfWork(UnitOfWorkBase):
    def __init__(self, session):
        self._session = session

    async def __aenter__(self):
        # self._session: AsyncSession = self._session_factory()
        self.users = UserRepository(self._session)
        return await super().__aenter__()

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self._session.close()

    async def _commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()
