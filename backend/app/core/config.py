from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_SECRET_KEY: str = "dev-secret-key"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    DATABASE_URL: str = "postgresql+asyncpg://phantom:phantom@localhost:5432/phantom"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Optional API keys
    NUMVERIFY_API_KEY: str = ""
    SHODAN_API_KEY: str = ""
    OPENCNAM_SID: str = ""
    OPENCNAM_AUTH_TOKEN: str = ""
    HIBP_API_KEY: str = ""
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_API_ID: str = ""
    TELEGRAM_API_HASH: str = ""

    PROXY_URL: str = ""
    PROXY_MODULES: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
