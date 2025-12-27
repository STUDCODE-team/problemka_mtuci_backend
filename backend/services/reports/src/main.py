from contextlib import asynccontextmanager

from fastapi import FastAPI

from common_lib.infrastructure.db.base import Base
from common_lib.infrastructure.db.engine import engine
from api.routes_reports import router as reports_router


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
