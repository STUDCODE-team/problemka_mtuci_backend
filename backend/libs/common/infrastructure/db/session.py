from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from .engine import engine

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as db:
        yield db
