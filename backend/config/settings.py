from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    # Auth fields (required)
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    FRONTEND_URL: str = "http://localhost:3000"
    REDIS_URL: str = "redis://redis:6379/0"
    # ETL fields (optional to avoid errors if unset)
    DATABASE_URL: str | None = "postgresql://postgres:password@timescaledb:5432/solar_db"
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
        extra='ignore',  # Ignore any unmatched vars
        case_sensitive=False
    )

    def __post_init__(self):
        # Debug: Print loaded env vars
        print("Loaded environment variables:", {k: v for k, v in os.environ.items() if k in self.model_fields})

settings = Settings()
print("Settings loaded:", settings.dict())