from fastapi import FastAPI

from app.api.routes_auth import router as auth_router

app = FastAPI(title="Auth Facade")
app.include_router(auth_router, prefix="/auth")
