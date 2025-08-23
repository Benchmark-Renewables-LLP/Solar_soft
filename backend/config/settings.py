from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    POSTGRES_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@timescaledb:5432/solar_db")
    JWT_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    class Config:
        env_file = ".env"

settings = Settings()