import logging

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.auth.dependencies import get_token_auth
from src.auth.exceptions import RefreshTokenNotValid
from src.core.security.jwt import JWTAuth, RefreshedTokens, TokenType
from src.user.uow import UserUnitOfWork
from src.user.exceptions import UserNotFound
from src.database.engine import async_session_maker


logger = logging.getLogger(__name__)


class JWTRefreshMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        pre_auth: JWTAuth = await get_token_auth(request=request)
        access_token_data = await pre_auth.read_token(TokenType.ACCESS)
        refreshed: RefreshedTokens | None = None

        if access_token_data is None:
            try:
                refreshed = await pre_auth.refresh_access_token()
            except RefreshTokenNotValid:
                logger.debug("Refresh token not valid", extra={"path": request.url.path})
                pass

        response = await call_next(request)

        if refreshed and not getattr(request.state, "auth_tokens_cleared", False):
            post_auth = await get_token_auth(
                request=request,
                response=response,
            )
            await post_auth.set_token(refreshed.access_token, TokenType.ACCESS)
            await post_auth.set_token(refreshed.refresh_token, TokenType.REFRESH)

        return response


class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth: JWTAuth = await get_token_auth(request=request)
        access_token_data = await auth.read_token(TokenType.ACCESS)
        if not access_token_data:
            request.state.user = None
            logger.debug("No access token provided", extra={"path": request.url.path})

        else:
            async with async_session_maker() as session:
                async with UserUnitOfWork(session) as uow:
                    try:
                        user = await uow.users.get_by_pk(access_token_data.user_id)
                    except UserNotFound:
                        logger.info(
                            "User from token not found",
                            extra={"user_id": str(access_token_data.user_id), "path": request.url.path},
                        )
                        user = None
                    request.state.user = user or None

        response = await call_next(request)
        return response
