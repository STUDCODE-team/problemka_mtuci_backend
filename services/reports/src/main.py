from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from common_lib.infrastructure.db.base import Base
from infrastructure.db import engine
from api.routes_reports import router as reports_router
from api.routes_categories import router as categories_router
from api.routes_notifications import router as notifications_router

# Import models so SQLAlchemy registers them with Base.metadata
import domain.models.db.report  # noqa: F401
import domain.models.db.report_comment  # noqa: F401
import domain.models.db.report_status_history  # noqa: F401
import domain.models.db.category  # noqa: F401
import domain.models.db.report_notification  # noqa: F401
import domain.models.db.push_subscription  # noqa: F401


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Reports microservice",
    lifespan=lifespan,
    debug=True,
    root_path="/api/reports",
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://[a-zA-Z0-9-]+\.problemka-mtuci\.tech",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        {"field": " -> ".join(str(loc) for loc in e["loc"][1:]), "message": e["msg"]}
        for e in exc.errors()
    ]
    response = JSONResponse(status_code=422, content={"detail": "Validation error", "errors": errors})
    origin = request.headers.get("origin")
    if origin and "problemka-mtuci.tech" in origin:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    return response


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


app.include_router(reports_router, prefix="/reports")
app.include_router(categories_router, prefix="/categories")
app.include_router(notifications_router, prefix="/notifications")
