from infrastructure.keycloak.keycloak_adapter import token_for_user


class LoginUseCase:
    def execute(self, username: str, password: str):
        return token_for_user(username, password)
