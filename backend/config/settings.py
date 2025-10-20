from pydantic_settings import BaseSettings, SettingsConfigDict
import os
import logging

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    JWT_SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    FRONTEND_URL: str = "http://localhost:3000"
    DATABASE_URL: str = "postgresql://postgres:password@timescaledb:5432/solar_db"
    REDIS_URL: str = "redis://redis:6379/0"
    SENDGRID_API_KEY: str | None = None
    COMPANY_KEY: str | None = None
    FLASK_ENV: str | None = "development"
    ENCRYPTION_KEY: str | None = None
    BATCH_SIZE: str | None = "100"
    SOLARMAN_EMAIL: str | None = None
    SOLARMAN_PASSWORD_SHA256: str | None = None
    SOLARMAN_APP_ID: str | None = None
    SOLARMAN_APP_SECRET: str | None = None

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
        case_sensitive=False
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logger.debug("Loaded environment variables: %s", {k: v for k, v in os.environ.items() if k in self.model_fields})
        logger.debug("DATABASE_URL: %s", self.DATABASE_URL)
        logger.debug("REDIS_URL: %s", self.REDIS_URL)
        logger.debug("SENDGRID_API_KEY: %s", self.SENDGRID_API_KEY)
        if "localhost" in self.DATABASE_URL:
            logger.warning("DATABASE_URL contains 'localhost'; overriding to 'timescaledb'")
            self.DATABASE_URL = "postgresql://postgres:password@timescaledb:5432/solar_db"

settings = Settings()
logger.debug("Settings loaded: %s", settings.dict())