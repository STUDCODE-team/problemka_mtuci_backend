from libs.common.config.settings import settings
from libs.common.utils.crypto import hash_value, verify_hash, generate_value
from services.auth.app.data.repositories.interfaces.otp_repository import OTPRepository


class OTPService:
    def __init__(self, otp_repository: OTPRepository):
        self.repo = otp_repository

    async def create_otp(self, email: str) -> str:
        if settings.GENERATE_DEFAULT_OTP:
            otp = "123456"
        else:
            otp = generate_value(6)

        otp_hash = hash_value(otp)
        await self.repo.save(email, otp_hash, settings.OTP_TTL_SEC)
        return otp

    async def verify_otp(self, email: str, code: str) -> bool:
        otp_hash = await self.repo.get(email)
        if not otp_hash:
            return False

        if not verify_hash(code, otp_hash):
            return False

        await self.repo.delete(email)
        return True
