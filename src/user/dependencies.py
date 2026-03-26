from typing import Annotated

from fastapi import Depends

from src.core.security.security import PasswordHasher
from src.database.engine import async_session_maker
from src.database.dependencies import SessionDep
from src.user.repository import UserRepository
from src.user.uow import UserUnitOfWork


def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()


async def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)


def get_user_uow() -> UserUnitOfWork:
    return UserUnitOfWork(async_session_maker)


PasswordHasherDep = Annotated[PasswordHasher, Depends(get_password_hasher)]
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
UserUOWDep = Annotated[UserUnitOfWork, Depends(get_user_uow)]
