# Формат URL:
# postgresql+psycopg2://username:password@host:port/database


from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.pool import NullPool

from libs.common.config.settings import settings

engine: Engine = create_engine(
    settings.database_url,
    echo=False,
    poolclass=NullPool,
)
