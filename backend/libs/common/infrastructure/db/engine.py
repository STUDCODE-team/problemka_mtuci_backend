from sqlalchemy.ext.asyncio import create_async_engine

from libs.common.config.settings import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True,
)
