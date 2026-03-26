import logging

from fastapi import FastAPI

from src.core.middleware.middleware import AuthenticationMiddleware, JWTRefreshMiddleware


logger = logging.getLogger(__name__)


def register_middleware(app: FastAPI):
    app.add_middleware(AuthenticationMiddleware)
    app.add_middleware(JWTRefreshMiddleware)
