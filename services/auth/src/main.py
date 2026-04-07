from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from common_lib.infrastructure.db.base import Base
from common_lib.infrastructure.db.engine import engine
from common_lib.infrastructure.redis.redis_client import init_redis
from api.routes_auth import router as auth_router
import domain.models.db.user_role  # noqa: F401  — регистрирует UserRoleRecord в Base.metadata


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


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    response = JSONResponse(status_code=500, content={"detail": str(exc)})
    origin = request.headers.get("origin")
    if origin and "problemka-mtuci.tech" in origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.get("/health")
async def health_check():
    return {"status": "ok"}

app.include_router(auth_router, prefix="/auth")
