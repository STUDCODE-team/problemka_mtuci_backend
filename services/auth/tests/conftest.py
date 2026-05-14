import os
import sys
from pathlib import Path

# Set env vars before any app imports so Settings() picks them up
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-key-at-least-32chars!!")
os.environ.setdefault("GENERATE_DEFAULT_OTP", "true")
os.environ.setdefault("AUTH_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("REPORTS_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("NOTIFICATIONS_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
os.environ.setdefault("REFRESH_TOKEN_EXPIRE_DAYS", "7")
os.environ.setdefault("OTP_TTL_SEC", "300")
os.environ.setdefault("COOKIE_SECURE", "false")
os.environ.setdefault("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:1")
os.environ.setdefault("INTERNAL_API_KEY", "test-internal-key")

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
