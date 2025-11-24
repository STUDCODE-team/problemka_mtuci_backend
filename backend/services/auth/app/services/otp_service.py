import redis.asyncio as redis

from libs.common.config.settings import settings
from libs.common.utils.crypto import hash_value, verify_hash, generate_value


class OTPService:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def create_otp(self, email: str) -> str:
        if settings.GENERATE_DEFAULT_OTP:
            otp = '123456'
        else:
            otp = generate_value(6)
        otp_hash = hash_value(otp)
        await self.redis.setex(f"otp:{email}", settings.OTP_TTL_SEC, otp_hash)
        return otp

    async def verify_otp(self, email: str, code: str) -> bool:
        otp_key = f"otp:{email}"
        otp_hash = await self.redis.get(otp_key)
        if not otp_hash:
            return False
        if not verify_hash(code, otp_hash.decode()):
            return False
        # Удаляем OTP после успешной проверки
        await self.redis.delete(otp_key)
        return True
