import logging
import os
import sys
from pathlib import Path

logging.disable(logging.WARNING)

os.environ.setdefault("JWT_SECRET", "test-jwt-secret-key-at-least-32chars!!")
os.environ.setdefault("AUTH_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("REPORTS_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("NOTIFICATIONS_DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
os.environ.setdefault("REFRESH_TOKEN_EXPIRE_DAYS", "7")
os.environ.setdefault("COOKIE_SECURE", "false")
os.environ.setdefault("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:1")
os.environ.setdefault("INTERNAL_API_KEY", "test-internal-key")

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
