from infrastructure.keycloak.keycloak_adapter import create_user


class RegisterUseCase:
    def execute(self, username: str, email: str, password: str):
        return create_user(username, email, password)
