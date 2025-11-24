from fastapi import FastAPI

from app.api.routes_auth import router as auth_router
from libs.common.infrastructure.db.base import Base
from libs.common.infrastructure.db.engine import engine
from libs.common.infrastructure.redis.redis_client import init_redis

app = FastAPI(title="Auth Facade")
app.include_router(auth_router, prefix="/auth")


@app.on_event("startup")
async def startup_event():
    await init_redis()

    Base.metadata.create_all(bind=engine)
