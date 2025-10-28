from fastapi import APIRouter

from .jwks_service import fetch_jwks

router = APIRouter()


@router.get("/.well-known/jwks.json")
async def jwks():
    return await fetch_jwks()
