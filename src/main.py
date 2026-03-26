import logging

from fastapi import FastAPI

from src.auth.router import router as auth_router
from src.core.exceptions import register_exception_handlers
from src.core.lifespan import lifespan
import src.core.logging_setup
from src.core.config import settings
from src.core.middleware import register_middleware
from src.user.router import router as user_router


logger = logging.getLogger(__name__)


app = FastAPI(
    title=settings.project_name, 
    lifespan=lifespan,
    # root_path="api",
)

register_exception_handlers(app)
register_middleware(app)

# Монтирование статических файлов
# app.mount("/static", StaticFiles(directory="/static"), name="static")

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(user_router, prefix="/api/users", tags=["users"])


def main():
    import uvicorn
    uvicorn.run(
        app="src.main:app", 
        host="0.0.0.0", 
        port=8000, 
        # reload=True,
        # workers=5,
    )


if __name__ == "__main__":
    main()
