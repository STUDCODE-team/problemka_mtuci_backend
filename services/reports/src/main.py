from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from common_lib.infrastructure.db.base import Base
from common_lib.infrastructure.db.engine import engine
from api.routes_reports import router as reports_router
from api.routes_categories import router as categories_router

# Import models so SQLAlchemy registers them with Base.metadata
import domain.models.db.report  # noqa: F401
import domain.models.db.report_comment  # noqa: F401
import domain.models.db.report_status_history  # noqa: F401
import domain.models.db.category  # noqa: F401


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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


app.include_router(reports_router, prefix="/reports")
app.include_router(categories_router, prefix="/categories")
