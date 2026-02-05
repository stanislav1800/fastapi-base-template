import logging
from pydantic import SecretStr

from src.auth.exceptions import InvalidCredentials
from src.core.security.jwt import JWTAuth
from src.core.security.security import PasswordHasher
from src.user.models import User
from src.user.uow import UserUnitOfWork

logger = logging.getLogger(__name__)


async def authenticate(
    email: str,
    password: SecretStr,
    pwd_hasher: PasswordHasher,
    uow: UserUnitOfWork,
    auth: JWTAuth,
) -> User:
    async with uow:
        user = await uow.users.get_by_email(email)

        if not pwd_hasher.verify(password.get_secret_value(), user.hashed_password):
            logger.info("Authentication failed: invalid credentials", extra={"email": email})
            raise InvalidCredentials()

        await auth.set_tokens(user)
        logger.info("Authentication succeeded", extra={"user_id": str(user.id), "email": user.email})
