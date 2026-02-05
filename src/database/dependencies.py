from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_async_session

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
