from dataclasses import asdict, dataclass
from datetime import timedelta
from enum import Enum
from typing import Any

import logging
import uuid6
from jose import JWTError, jwt
from starlette.requests import Request
from starlette.responses import Response

from src.auth.exceptions import AccessTokenNotValid, RefreshTokenNotValid
from src.auth.infrastructure.token_storage.base import TokenData, TokenStorageBase
from src.auth.infrastructure.transports.base import AuthTransportBase
from src.core.config import settings
from src.integration.utils.datetimes import get_timezone_now
from src.user.models import User

logger = logging.getLogger(__name__)


class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"

@dataclass(frozen=True)
class RefreshedTokens:
    access_token: str
    refresh_token: str


class JWTProvider:
    def __init__(self):
        self.secret_key = settings.secret_key.get_secret_value()
        self.algorithm = settings.algorithm
        self.access_exp = settings.access_token_expires_seconds
        self.refresh_exp = settings.refresh_token_expire_seconds
        self.jwt_issuer = settings.jwt_issuer

        if not self.secret_key:
            raise ValueError("Secret keys not configured")

    def create_access_token(self, data: dict, algorithm: str | None = None, access_exp: int | None = None) -> str:
        if access_exp is None:
            access_exp = self.access_exp

        return self._encode_jwt(
            data=data,
            algorithm=algorithm,
            lifetime_seconds=access_exp,
        )

    def create_refresh_token(self, data: dict, algorithm: str | None = None, refresh_exp: int | None = None) -> str:
        if refresh_exp is None:
            refresh_exp = self.refresh_exp

        return self._encode_jwt(
            data=data,
            algorithm=algorithm,
            lifetime_seconds=refresh_exp,
        )

    def _encode_jwt(
        self,
        data: dict,
        algorithm: str | None,
        lifetime_seconds: int | None = None,
    ) -> str:
        payload = data.copy()
        if algorithm is None:
            algorithm = self.algorithm

        expire = get_timezone_now() + timedelta(seconds=lifetime_seconds)
        payload["jti"] = str(uuid6.uuid6())
        payload["iss"] = self.jwt_issuer
        payload["exp"] = int(expire.timestamp())

        return jwt.encode(
            payload,
            key=self.secret_key,
            algorithm=algorithm,
        )

    def read_token(
        self,
        token: str | None,
        algorithms: list[str] | None = None,
    ) -> TokenData | None:
        if token is None:
            return None

        try:
            data = self._decode_jwt(
                token,
                algorithms=algorithms,
            )
            user_id = data.get("user_id")
            if user_id is None:
                return None
            return TokenData(**data)
        except JWTError:
            return None

    def _decode_jwt(
        self,
        encoded_jwt: str,
        algorithms: list[str] | None,
    ) -> dict[str, Any]:
        if algorithms is None:
            algorithms = [self.algorithm]

        return jwt.decode(
            token=encoded_jwt,
            key=self.secret_key,
            algorithms=algorithms,
            issuer=self.jwt_issuer,
        )


class JWTAuth:
    def __init__(
        self,
        token_provider: JWTProvider,
        transports: dict[TokenType, list[AuthTransportBase]],
        token_storage: TokenStorageBase | None = None,
        request: Request | None = None,
        response: Response | None = None,
    ):
        self.token_provider = token_provider
        self.transports = transports
        self.token_storage = token_storage
        self.request = request
        self.response = response

    async def set_tokens(self, user: User) -> RefreshedTokens:
        data = {
            "user_id": str(user.id),
            "is_superuser": user.is_superuser,
        }
        access_token = self.token_provider.create_access_token(data)
        refresh_token = self.token_provider.create_refresh_token(data)
        await self.set_token(access_token, TokenType.ACCESS)
        await self.set_token(refresh_token, TokenType.REFRESH)
        logger.info("Tokens set", extra={"user_id": str(user.id)})
        return RefreshedTokens(
            access_token=access_token,
            refresh_token=refresh_token,
        )


    async def set_token(self, token: str, token_type: TokenType) -> None:
        for transport in self._get_transports(token_type):
            transport.set_token(self.response, token)

        if self.token_storage:
            await self.token_storage.store_token(self.token_provider.read_token(token))

    async def unset_tokens(self) -> None:
        access_token_data = await self.read_token(TokenType.ACCESS)
        if not access_token_data:
            raise AccessTokenNotValid()

        if self.token_storage:
            await self.token_storage.revoke_tokens_by_user(access_token_data.user_id)

        for token_type, transports in self.transports.items():
            for transport in transports:
                transport.delete_token(self.response)

        logger.info("Tokens unset", extra={"user_id": str(access_token_data.user_id)})

    async def refresh_access_token(self) -> RefreshedTokens:
        refresh_token_data = await self.read_token(TokenType.REFRESH)

        if not refresh_token_data:
            raise RefreshTokenNotValid()

        if self.token_storage:
            access_token_data = await self.read_token(TokenType.ACCESS)
            
            if access_token_data:
                await self.token_storage.revoke_tokens_by_jti(refresh_token_data.jti, str(refresh_token_data.user_id))
                await self.token_storage.revoke_tokens_by_jti(access_token_data.jti, str(access_token_data.user_id))

        data = asdict(refresh_token_data)

        access_token = self.token_provider.create_access_token(data)
        refresh_token = self.token_provider.create_refresh_token(data)

        self.request.state.access_token = access_token

        if self.token_storage:
            await self.token_storage.store_token(self.token_provider.read_token(access_token))
            await self.token_storage.store_token(self.token_provider.read_token(refresh_token))

        if self.response:
            for transport in self._get_transports(TokenType.ACCESS):
                transport.set_token(self.response, access_token)

            for transport in self._get_transports(TokenType.REFRESH):
                transport.set_token(self.response, refresh_token)

        return RefreshedTokens(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def read_token(self, token_type: TokenType) -> TokenData | None:
        token = self._get_access_token() if token_type == TokenType.ACCESS else self._get_refresh_token()
        token_data = self.token_provider.read_token(token)
        return await self._validate_token_or_none(token_data)

    async def _validate_token_or_none(self, token_data: TokenData) -> TokenData | None:
        if not token_data:
            return None
        
        if token_data.jti and self.token_storage:
            is_active = await self.token_storage.is_token_active(token_data.jti)
            if not is_active:
                return None
        return token_data

    def _get_access_token(self) -> str | None:
        if hasattr(self.request.state, "access_token"):
            return self.request.state.access_token
        
        for transport in self._get_transports(TokenType.ACCESS):
            token = transport.get_token(self.request)
            if token is not None:
                return token

    def _get_refresh_token(self) -> str | None:
        for transport in self._get_transports(TokenType.REFRESH):
            token = transport.get_token(self.request)
            if token is not None:
                return token

    def _get_transports(self, transport_type: TokenType) -> list[AuthTransportBase]:
        return self.transports.get(transport_type, [])
