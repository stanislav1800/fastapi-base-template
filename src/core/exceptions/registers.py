import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.core.exceptions.exceptions import AppException


logger = logging.getLogger(__name__)


async def app_exception_handler(request: Request, exc: AppException):
    logger.warning(
        "Handled application exception",
        extra={"status_code": exc.status_code, "detail": exc.detail, "path": request.url.path},
    )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail, **(exc.extra or {})})


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(AppException, app_exception_handler)
