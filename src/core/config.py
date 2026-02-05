from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Api
    project_name: str = "UNNAMED PROJECT"
    LOG_LEVEL: str = "INFO"

    # Jwt
    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expires_seconds: int = 60 * 15
    refresh_token_expire_seconds: int = 60 * 60 * 24 * 30
    access_token_transport: Literal["header", "cookie", "all", "none"] = "header"
    refresh_token_transport: Literal["header", "cookie", "all", "none"] = "cookie"
    access_token_cookie_name: str = "access_token"
    refresh_token_cookie_name: str = "refresh_token"
    access_token_header_name: str = "authorization"
    refresh_token_header_name: str = "X-Refresh-Token"
    jwt_header_type: str = "Bearer"
    jwt_issuer: str = "auth-service"

    # Database
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # Redis
    redis_url: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def get_db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    def get_db_url_for_alembic(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
