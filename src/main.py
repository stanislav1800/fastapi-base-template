import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.auth.router import router as auth_router
import src.core.logging_setup
from src.core.config import settings
from src.core.exceptions import AppException
from src.core.infrastructure.redis_client import close_redis, init_redis
from src.core.middleware import AuthenticationMiddleware, JWTRefreshMiddleware
from src.user.router import router as user_router


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup
    logger.info("Starting application")
    await init_redis()
    yield
    # on shutdown
    logger.info("Shutting down application")
    await close_redis()


app = FastAPI(title=settings.project_name, lifespan=lifespan)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    logger.warning(
        "Handled application exception",
        extra={"status_code": exc.status_code, "detail": exc.detail, "path": request.url.path},
    )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail, **(exc.extra or {})})


app.add_middleware(AuthenticationMiddleware)
app.add_middleware(JWTRefreshMiddleware)

# Монтирование статических файлов
# app.mount("/static", StaticFiles(directory="/static"), name="static")

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(user_router, prefix="/api/users", tags=["users"])


def main():
    import uvicorn

    """Функция, которая будет вызвана командой `startapp` из терминала"""
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
