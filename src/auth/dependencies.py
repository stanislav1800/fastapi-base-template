from typing import Annotated

from fastapi import Depends
from starlette.requests import Request
from starlette.responses import Response

from src.auth.infrastructure.token_storage.base import TokenStorageBase
from src.auth.infrastructure.token_storage.redis import RedisTokenStorage
from src.core.infrastructure.redis_client import get_redis
from src.auth.infrastructure.transports.base import AuthTransportBase
from src.auth.infrastructure.transports.cookie import CookieTransport
from src.auth.infrastructure.transports.header import HeaderTransport
from src.core.config import settings
from src.core.security.jwt import JWTAuth, JWTProvider, TokenType
from src.core.security.security import PasswordHasher


def get_password_hasher() -> PasswordHasher:
    return PasswordHasher()


def get_token_storage() -> TokenStorageBase:
    # При прямом вызове внутри приложения используем глобальный клиент.
    # RedisTokenStorage поддерживает получение клиента через конструктор,
    # но по умолчанию использует глобальный `get_redis()`.
    return RedisTokenStorage()


async def get_token_auth(
    request: Request,
    response: Response = None,
) -> JWTAuth:
    jwt_provider = JWTProvider()

    access_transports: list[AuthTransportBase] = []
    if settings.access_token_transport in ["cookie", "all"]:
        access_transports.append(
            CookieTransport(
                cookie_name=settings.access_token_cookie_name,
                cookie_max_age=settings.access_token_expires_seconds,
                cookie_secure=True,
                cookie_httponly=True,
                cookie_samesite="lax",
            )
        )
    if settings.access_token_transport in ["header", "all"]:
        access_transports.append(
            HeaderTransport(
                header_name=settings.access_token_header_name,
                token_type_prefix=settings.jwt_header_type,
            )
        )

    refresh_transports: list[AuthTransportBase] = []
    if settings.refresh_token_transport in ["cookie", "all"]:
        refresh_transports.append(
            CookieTransport(
                cookie_name=settings.refresh_token_cookie_name,
                cookie_max_age=settings.refresh_token_expire_seconds,
                cookie_secure=True,
                cookie_httponly=True,
                cookie_samesite="lax",
            )
        )
    if settings.refresh_token_transport in ["header", "all"]:
        refresh_transports.append(
            HeaderTransport(
                header_name=settings.refresh_token_header_name,
                token_type_prefix=settings.jwt_header_type,
            )
        )

    transports = {
        TokenType.ACCESS: access_transports,
        TokenType.REFRESH: refresh_transports,
    }

    return JWTAuth(jwt_provider, transports, get_token_storage(), request=request, response=response)


TokenAuthDep = Annotated[JWTAuth, Depends(get_token_auth)]
TokenStorageDep = Annotated[TokenStorageBase, Depends(get_token_storage)]
PasswordHasherDep = Annotated[PasswordHasher, Depends(get_password_hasher)]
