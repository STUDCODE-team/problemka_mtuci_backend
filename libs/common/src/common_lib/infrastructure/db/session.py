from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .engine import engine

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

from typing import AsyncGenerator

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session