import logging
from uuid import UUID

from src.core.security.security import PasswordHasher
from src.user.models import User
from src.user.schemas import UserCreate, UserCreateBody, UserUpdate, UserUpdateBody
from src.user.uow import UserUnitOfWork

logger = logging.getLogger(__name__)


async def register_user(
    user_data: UserCreateBody,
    pwd_hasher: PasswordHasher,
    uow: UserUnitOfWork,
) -> User:
    user_data = UserCreate(**user_data.model_dump(mode="json"), hashed_password=pwd_hasher.hash(user_data.password))
    async with uow:
        new_user = await uow.users.add(user_data)
        await uow.commit()

    logger.info("User registered", extra={"user_id": str(new_user.id), "email": new_user.email})
    return new_user


async def get_user_profile(
    user_pk: UUID,
    uow: UserUnitOfWork,
):
    async with uow:
        user = await uow.users.get_by_pk(user_pk)

    logger.info("User profile retrieved", extra={"user_id": str(user_pk)})
    return user


async def update_user(
    user_pk: UUID,
    user_data: UserUpdateBody,
    uow: UserUnitOfWork,
) -> User:
    user_data = UserUpdate(
        id=user_pk,
        **user_data.model_dump(mode="json"),
    )
    async with uow:
        user = await uow.users.update(user_data)
        await uow.commit()

    logger.info("User updated", extra={"user_id": str(user.id)})
    return user


async def delete_user(
    user_pk: UUID,
    uow: UserUnitOfWork,
) -> None:
    async with uow:        
        await uow.users.delete(user_pk)
        await uow.commit()

    logger.info("User deleted", extra={"user_id": str(user_pk)})
