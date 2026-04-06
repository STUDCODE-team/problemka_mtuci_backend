from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from common_lib.infrastructure.db.base import Base
from common_lib.infrastructure.db.engine import engine
from common_lib.infrastructure.redis.redis_client import init_redis
from api.routes_auth import router as auth_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_redis()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Auth Facade",
    lifespan=lifespan,
    root_path="/api/auth",
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://[a-zA-Z0-9-]+\.problemka-mtuci\.tech",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}

app.include_router(auth_router, prefix="/auth")
