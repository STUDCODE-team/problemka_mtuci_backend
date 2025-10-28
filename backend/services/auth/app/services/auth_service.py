# auth/app/services/auth_service.py
from app.use_cases.login import LoginUseCase
from app.use_cases.logout import LogoutUseCase
from app.use_cases.refresh import RefreshUseCase
from app.use_cases.register import RegisterUseCase
from libs.common.domain.auth.i_auth_service import IAuthService


class AuthService(IAuthService):
    def __init__(self):
        self.login_uc = LoginUseCase()
        self.register_uc = RegisterUseCase()
        self.refresh_uc = RefreshUseCase()
        self.logout_uc = LogoutUseCase()

    def login(self, username: str, password: str):
        return self.login_uc.execute(username, password)

    def register(self, username: str, email: str, password: str):
        return self.register_uc.execute(username, email, password)

    def refresh(self, refresh_token_str: str):
        return self.refresh_uc.execute(refresh_token_str)

    def logout(self, refresh_token_str: str):
        return self.logout_uc.execute(refresh_token_str)
