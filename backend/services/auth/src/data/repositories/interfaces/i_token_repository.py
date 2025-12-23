from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID


class TokenProvider(ABC):
    @abstractmethod
    def create_access_token(self, user_id: str, role: str, expires_at: datetime) -> str:
        pass

    @abstractmethod
    def create_refresh_token(self, jti: UUID, user_id: str, expires_at: datetime) -> str:
        pass

    @abstractmethod
    def decode_and_verify(self, token: str) -> dict:
        pass

    @abstractmethod
    def decode_access_token(self, token: str) -> dict:
        pass

    @abstractmethod
    def decode_refresh_token(self, token: str) -> dict:
        pass
