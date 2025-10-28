from infrastructure.keycloak.keycloak_adapter import logout


class LogoutUseCase:
    def execute(self, refresh_token: str):
        return logout(refresh_token)
