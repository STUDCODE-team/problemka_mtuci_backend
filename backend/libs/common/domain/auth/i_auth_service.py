from abc import ABC, abstractmethod


class IAuthService(ABC):

    @abstractmethod
    def request_otp(self, username, password):
        pass

    @abstractmethod
    def verify_otp(self, refresh_token):
        pass

    @abstractmethod
    def refresh(self, username, email, password):
        pass

    @abstractmethod
    def logout(self, refresh_token):
        pass
