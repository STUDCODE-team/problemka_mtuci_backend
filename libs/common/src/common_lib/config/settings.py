from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path("/app/.env")


class Settings(BaseSettings):
    DATABASE_URL: str = ''
    REDIS_URL: str = ''
    JWT_SECRET: str = ''
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    OTP_TTL_SEC: int = 300
    GENERATE_DEFAULT_OTP: bool = False

    model_config = SettingsConfigDict(
        env_file=BASE_DIR,
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()
