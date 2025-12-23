from contextlib import asynccontextmanager

from fastapi import FastAPI

from libs.common.infrastructure.db.base import Base
from libs.common.infrastructure.db.engine import engine
from services.reports.app.api.routes_reports import router as reports_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

    print("Application shutting down")


app = FastAPI(
    title="Reports microservice",
    lifespan=lifespan,
    debug=True,
)

app.include_router(reports_router, prefix="/reports")
