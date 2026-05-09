from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_fastapi_instrumentator import Instrumentator

from common_lib.infrastructure.db.base import Base
from common_lib.infrastructure.db.engine import engine
from common_lib.infrastructure.logging import setup_logging
from common_lib.infrastructure.redis.redis_client import init_redis
from common_lib.infrastructure.telemetry import setup_telemetry
from common_lib.infrastructure.origin_middleware import OriginCheckMiddleware
from common_lib.infrastructure.trace_middleware import TraceIdMiddleware
from common_lib.messaging import producer
from common_lib.config.settings import settings
from common_lib.utils.trace import get_or_create_trace_id
from api.routes_auth import router as auth_router
import domain.models.db.user_role  # noqa: F401  — регистрирует UserRoleRecord в Base.metadata

setup_logging("auth")
setup_telemetry("auth")


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_redis()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await producer.init_producer(settings.RABBITMQ_URL)
    yield
    await producer.close_producer()


app = FastAPI(
    title="Auth Facade",
    lifespan=lifespan,
    root_path="/api/auth",
)

app.add_middleware(OriginCheckMiddleware)
app.add_middleware(TraceIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://[a-zA-Z0-9-]+\.problemka-mtuci\.tech",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    trace_id = get_or_create_trace_id(request)
    response = JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "traceId": trace_id},
        headers=exc.headers,
    )
    response.headers["X-Trace-Id"] = trace_id
    origin = request.headers.get("origin")
    if origin and "problemka-mtuci.tech" in origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    trace_id = get_or_create_trace_id(request)
    errors = [
        {"field": " -> ".join(str(loc) for loc in e["loc"][1:]), "message": e["msg"]}
        for e in exc.errors()
    ]
    response = JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": errors, "traceId": trace_id},
    )
    response.headers["X-Trace-Id"] = trace_id
    origin = request.headers.get("origin")
    if origin and "problemka-mtuci.tech" in origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    trace_id = get_or_create_trace_id(request)
    response = JSONResponse(status_code=500, content={"detail": str(exc), "traceId": trace_id})
    response.headers["X-Trace-Id"] = trace_id
    origin = request.headers.get("origin")
    if origin and "problemka-mtuci.tech" in origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


@app.get("/health")
async def health_check():
    return {"status": "ok"}

app.include_router(auth_router)

Instrumentator().instrument(app).expose(app)
FastAPIInstrumentor.instrument_app(app)
