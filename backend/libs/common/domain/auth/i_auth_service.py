from abc import ABC, abstractmethod


class IAuthService(ABC):

    @abstractmethod
    def login(self, username, password):
        pass

    @abstractmethod
    def logout(self, refresh_token):
        pass

    @abstractmethod
    def register(self, username, email, password):
        pass

    @abstractmethod
    def refresh(self, refresh_token):
        pass
