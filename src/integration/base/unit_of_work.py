from abc import ABC, abstractmethod
from typing import Self


class UnitOfWorkBase(ABC):
    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args):
        await self.rollback()

    async def commit(self):
        await self._commit()

    @abstractmethod
    async def rollback(self):
        pass

    @abstractmethod
    async def _commit(self):
        pass
