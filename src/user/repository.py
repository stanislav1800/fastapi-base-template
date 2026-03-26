import logging
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from src.user.exceptions import UserAlreadyExists, UserNotFound
from src.user.models import User as UserDB
from src.user.schemas import User, UserCreate, UserUpdate

logger = logging.getLogger(__name__)


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, user: UserCreate) -> User:
        obj = UserDB(**user.model_dump(mode="json"))
        self.session.add(obj)

        try:
            await self.session.flush()
        except IntegrityError as e:
            try:
                detail = "User can't be created. " + str(e.orig).split('\nDETAIL:  ')[1]
            except IndexError:
                detail = "User can't be created due to integrity error."
            raise UserAlreadyExists(detail=detail)

        created = self._to_domain(obj)
        logger.info("User stored", extra={"user_id": str(created.id), "email": created.email})
        return created

    async def get_by_pk(self, pk: UUID) -> User:
        obj: UserDB | None = await self.session.get(UserDB, pk)

        if not obj:
            logger.debug("User not found by id", extra={"user_id": str(pk)})
            raise UserNotFound(detail=f"User with uuid {pk} not found")

        return self._to_domain(obj)

    async def get_by_email(self, email: str) -> User:
        stmt = select(UserDB).where(UserDB.email == email)
        result = await self.session.execute(stmt)
        obj: UserDB | None = result.scalar_one_or_none()

        if obj is None:
            logger.debug("User not found by email", extra={"email": email})
            raise UserNotFound(detail=f"User with email {email} not found")

        return self._to_domain(obj)

    async def update(self, user_data: UserUpdate) -> User:
        stmt = select(UserDB).where(UserDB.id == user_data.id)
        result = await self.session.execute(stmt)
        obj: UserDB = result.scalar_one_or_none()

        if not obj:
            logger.debug("User not found for update", extra={"user_id": str(user_data.id)})
            raise UserNotFound(detail=f"User with id {user_data.id} not found")

        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)  

        await self.session.flush()

        updated = self._to_domain(obj)
        logger.info("User updated in storage", extra={"user_id": str(updated.id)})
        return updated

    async def update_password(self, pk: UUID, hashed_password: str):
        stmt = select(UserDB).where(UserDB.id == pk)
        result = await self.session.execute(stmt)
        obj: UserDB = result.scalar_one_or_none()

        if not obj:
            logger.debug("User not found for update", extra={"pk": str(pk)})
            raise UserNotFound(detail=f"User with id {pk} not found")

        obj.hashed_password = hashed_password
        await self.session.flush()

        return self._to_domain(obj)

    async def delete(self, pk: int):
        obj = await self.session.get(UserDB, pk)

        if not obj:
            logger.debug("User not found for delete", extra={"user_id": str(pk)})
            raise UserNotFound(detail=f"User with id {pk} not found")

        await self.session.delete(obj)
        logger.info("User deleted from storage", extra={"user_id": str(pk)})
    
    @staticmethod
    def _to_domain(obj: UserDB) -> User:
        return User(
            id=obj.id,
            email=obj.email,
            hashed_password=obj.hashed_password,
            is_active=obj.is_active,
            is_superuser=obj.is_superuser,
            is_verified=obj.is_verified,
            created_at=obj.created_at,
        )
