import abc
from dataclasses import dataclass
from uuid import UUID


@dataclass(kw_only=True)
class TokenData:
    user_id: UUID
    is_superuser: bool = False
    exp: int
    jti: str | None = None
    aut: str | None = None
    iss: str | None = None


class TokenStorageBase(abc.ABC):
    """Redis-based implementation of ITokenStorage.

    Stores JWT token metadata for validation and revocation.
    Each token is stored by its JTI and associated with a user for mass revocation.
    """

    @abc.abstractmethod
    async def store_token(self, token_data: TokenData) -> None:
        """Store the token metadata in Redis.

        :param token_data: The decoded token data including expiration and JTI.
        """
        pass

    @abc.abstractmethod
    async def revoke_tokens_by_user(self, user_id: str) -> None:
        """Revoke all tokens associated with a specific user.

        :param user_id: The ID of the user whose tokens should be revoked.
        """
        pass

    @abc.abstractmethod
    async def is_token_active(self, jti: str) -> bool:
        """Check if a token with the given JTI is still active (not revoked or expired).

        :param jti: JWT ID of the token.
        :return: True if the token is active, False otherwise.
        """
        pass

    @abc.abstractmethod
    async def revoke_tokens_by_jti(self, jti: str, user_id: str):
        pass
