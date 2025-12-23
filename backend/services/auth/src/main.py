from contextlib import asynccontextmanager

from fastapi import FastAPI

from libs.common.infrastructure.db.base import Base
from libs.common.infrastructure.db.engine import engine
from libs.common.infrastructure.redis.redis_client import init_redis
from services.auth.src.api.routes_auth import router as auth_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Startup
    await init_redis()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

    print("Application shutting down")


app = FastAPI(
    title="Auth Facade",
    lifespan=lifespan,
    debug=True,
)

app.include_router(auth_router, prefix="/auth")
