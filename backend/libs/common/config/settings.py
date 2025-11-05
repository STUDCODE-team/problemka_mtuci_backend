from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    database_url: str = ''
    redis_url: str = ''
    jwt_secret: str = ''
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    otp_ttl_sec: int = 300
    smtp_host: str = "smtp.example.com"
    smtp_port: int = 587
    smtp_password: str = "your_password"
    from_email: str = "your_email@example.com"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()
