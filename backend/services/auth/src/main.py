from contextlib import asynccontextmanager

from fastapi import FastAPI

from common_lib.infrastructure.db.base import Base
from common_lib.infrastructure.db.engine import engine
from common_lib.infrastructure.redis.redis_client import init_redis
from api.routes_auth import router as auth_router


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
    root_path="/api/auth",
)

app.include_router(auth_router, prefix="/auth")
