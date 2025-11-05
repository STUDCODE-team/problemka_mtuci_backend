from abc import ABC, abstractmethod


class IAuthService(ABC):

    @abstractmethod
    def request_otp(self, email):
        pass

    @abstractmethod
    def verify_otp(self, email, code):
        pass

    @abstractmethod
    def refresh(self, refresh_token):
        pass

    @abstractmethod
    def logout(self, refresh_token):
        pass
