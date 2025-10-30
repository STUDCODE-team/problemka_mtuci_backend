from app.use_cases.logout import LogoutUseCase
from app.use_cases.refresh import RefreshUseCase
from app.use_cases.request_otp import RequestOtpUseCase
from app.use_cases.verify_otp import VerifyOtpUseCase
from libs.common.domain.auth.i_auth_service import IAuthService


class AuthService(IAuthService):
    def __init__(self):
        self.request_otp_uc = RequestOtpUseCase()
        self.verify_otp_uc = VerifyOtpUseCase()
        self.refresh_uc = RefreshUseCase()
        self.logout_uc = LogoutUseCase()

    def request_otp(self, email: str):
        return self.request_otp_uc.execute(email)

    def verify_otp(self, email: str, code: str):
        return self.verify_otp_uc.execute(email, code)

    def refresh(self, refresh_token: str):
        return self.refresh_uc.execute(refresh_token)

    def logout(self, refresh_token: str):
        return self.logout_uc.execute(refresh_token)
