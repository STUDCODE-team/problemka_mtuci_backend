from infrastructure.keycloak.keycloak_adapter import refresh_access_token


class RefreshUseCase:
    def execute(self, refresh_token: str):
        return refresh_access_token(refresh_token)
