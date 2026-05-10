from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path("/app/.env")


class Settings(BaseSettings):
    AUTH_DATABASE_URL: str = ''
    REPORTS_DATABASE_URL: str = ''
    NOTIFICATIONS_DATABASE_URL: str = ''
    AUTH_REDIS_URL: str = ''
    NOTIFICATION_SERVICE_URL: str = 'http://notification-service:8000'
    RABBITMQ_URL: str = 'amqp://guest:guest@rabbitmq:5672/'
    # Shared secret for internal service-to-service calls (header: X-Internal-Secret)
    INTERNAL_API_KEY: str = ''
    JWT_SECRET: str = ''
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    OTP_TTL_SEC: int = 300
    GENERATE_DEFAULT_OTP: bool = False

    SMTP_HOST: str = 'smtp.gmail.com'
    SMTP_PORT: int = 587
    SMTP_USER: str = ''
    SMTP_PASSWORD: str = ''
    SMTP_FROM: str = ''

    # Web Push (VAPID) — generate with: vapid --gen
    # Store base64url-encoded DER keys
    VAPID_PRIVATE_KEY: str = ''
    VAPID_PUBLIC_KEY: str = ''
    VAPID_CONTACT_EMAIL: str = 'admin@problemka-mtuci.tech'

    # Cookie security
    COOKIE_SECURE: bool = True
    # Browser-visible path prefix for the auth service (used to scope refresh_token cookie)
    COOKIE_REFRESH_PATH: str = '/api/auth'

    model_config = SettingsConfigDict(
        env_file=BASE_DIR,
        env_file_encoding="utf-8",
        case_sensitive=False
    )


settings = Settings()
