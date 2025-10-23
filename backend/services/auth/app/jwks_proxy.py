from fastapi import APIRouter
from keycloak_facade import fetch_jwks

router = APIRouter()

@router.get("/.well-known/jwks.json")
async def jwks():
    return await fetch_jwks()
