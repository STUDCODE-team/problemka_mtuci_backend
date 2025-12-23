from typing import Optional

import redis

from services.auth.src.data.repositories.interfaces.i_otp_repository import OTPRepository


class RedisOTPRepository(OTPRepository):
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def save(self, email: str, otp_hash: str, ttl: int) -> None:
        await self.redis.setex(f"otp:{email}", ttl, otp_hash)

    async def get(self, email: str) -> Optional[str]:
        value = await self.redis.get(f"otp:{email}")
        return value.decode() if value else None

    async def delete(self, email: str) -> None:
        await self.redis.delete(f"otp:{email}")
