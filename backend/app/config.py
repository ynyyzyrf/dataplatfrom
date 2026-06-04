"""Application configuration management.

Uses pydantic-settings for type-safe configuration loaded from
environment variables or a .env file.
"""

from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import Annotated

from dotenv import load_dotenv
from pydantic import AliasChoices, AnyHttpUrl, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env file if present
_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
if _ENV_PATH.exists():
    load_dotenv(_ENV_PATH)


class Settings(BaseSettings):
    """Global application settings."""

    model_config = SettingsConfigDict(
        env_prefix="GDP_",
        env_file=(".env", ".env.local"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # -- General -----------------------------------------------------------
    app_name: str = "GeneralDataPlatform"
    app_version: str = "0.1.0"
    debug: bool = False

    # -- Database ----------------------------------------------------------
    # e.g. postgresql+asyncpg://user:pass@localhost:5432/gdp
    database_url: SecretStr = Field(
        default=SecretStr("postgresql+asyncpg://postgres:postgres@localhost:5432/gdp"),
    )
    # Sync engine URL (Alembic / SQLAlchemy sync ops)
    database_sync_url: SecretStr = Field(
        default=SecretStr("postgresql://postgres:postgres@localhost:5432/gdp"),
    )
    database_pool_size: int = 10
    database_max_overflow: int = 20
    database_echo: bool = False

    # -- Redis -------------------------------------------------------------
    redis_url: str = "redis://localhost:6379/0"

    # -- JWT / Auth --------------------------------------------------------
    jwt_secret: SecretStr = Field(
        default=SecretStr("CHANGE-ME-IN-PRODUCTION-USE-STRONG-RANDOM"),
    )
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # -- Encryption (Fernet) for credentials -------------------------------
    encryption_key: SecretStr = Field(
        default=SecretStr(""),
        description="43-byte Fernet key. Generate with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'",
    )

    # -- CORS --------------------------------------------------------------
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:5175",
            "http://localhost:5176",
            "http://localhost:3000",
        ],
    )

    # -- Celery / Broker ---------------------------------------------------
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # -- Storage -----------------------------------------------------------
    storage_local_root: str = str(Path("./storage") / "uploads")
    storage_max_component_bundle_size_mb: int = 10

    # -- SSRF guard --------------------------------------------------------
    ssrf_block_private_ranges: bool = True
    ssrf_allow_list: list[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("ssrf_allow_domains", "ssrf_allow_list"),
    )

    @cached_property
    def encryption_key_bytes(self) -> bytes:
        key = self.encryption_key.get_secret_value()
        if not key:
            # Fallback for local dev — NEVER use in production
            from cryptography.fernet import Fernet
            return Fernet.generate_key()
        return key.encode()

    @property
    def database_url_plain(self) -> str:
        return self.database_url.get_secret_value()

    @property
    def database_sync_url_plain(self) -> str:
        return self.database_sync_url.get_secret_value()


settings = Settings()
