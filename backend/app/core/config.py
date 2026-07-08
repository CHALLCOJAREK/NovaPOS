from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ==================================================
    # Application
    # ==================================================

    APP_NAME: str = Field(default="NovaPOS API")
    APP_VERSION: str = Field(default="0.1.0")
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)

    # ==================================================
    # Store / Tenant Configuration
    # ==================================================

    DEFAULT_TENANT_ID: str = Field(default="danae")
    DEFAULT_STORE_ID: str = Field(default="danae")
    STORE_NAME: str = Field(default="Tienda de Abarrotes Danae")

    # ==================================================
    # Paths
    # ==================================================

    DATA_PATH: str = Field(default="data")
    TENANT_DATA_PATH: str = Field(default="data/Danae")
    UPLOAD_PATH: str = Field(default="data/Danae/uploads")
    BACKUP_PATH: str = Field(default="data/Danae/backups")

    # ==================================================
    # Database
    # ==================================================

    DATABASE_TYPE: str = Field(default="sqlite")
    DATABASE_URL: str = Field(default="sqlite:///./data/Danae/database.db")

    # ==================================================
    # Security / JWT
    # ==================================================

    SECRET_KEY: str
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60)
    REFRESH_TOKEN_EXPIRE_MINUTES: int = Field(default=10080)

    # ==================================================
    # Password Hashing
    # ==================================================

    PASSWORD_HASH_SCHEME: str = Field(default="bcrypt")

    # ==================================================
    # CORS
    # ==================================================

    BACKEND_CORS_ORIGINS: str = Field(
        default="http://localhost:4200,http://127.0.0.1:4200"
    )

    # ==================================================
    # Initial Admin User
    # ==================================================

    INITIAL_ADMIN_USERNAME: str = Field(default="admin")
    INITIAL_ADMIN_EMAIL: str = Field(default="admin@novapos.local")
    INITIAL_ADMIN_PASSWORD: str = Field(default="Admin123456")
    INITIAL_ADMIN_FULL_NAME: str = Field(default="Administrador NovaPOS")

    # ==================================================
    # Audit / Logs
    # ==================================================

    LOG_LEVEL: str = Field(default="INFO")
    ENABLE_AUDIT_LOG: bool = Field(default=True)

    # ==================================================
    # Backups
    # ==================================================

    ENABLE_AUTOMATIC_BACKUPS: bool = Field(default=True)
    BACKUP_RETENTION_DAYS: int = Field(default=30)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def cors_origins(self) -> List[str]:
        return [
            origin.strip()
            for origin in self.BACKEND_CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()