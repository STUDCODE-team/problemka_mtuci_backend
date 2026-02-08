from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID


class IRefreshTokenRepository(ABC):
    @abstractmethod
    async def save(self, user_id: UUID, raw_token: str, jti: str, expires_at: datetime) -> None:
        pass

    @abstractmethod
    async def find_active_by_jti(self, jti: str) -> object | None:
        pass

    @abstractmethod
    async def revoke_by_jti(self, jti: str) -> None:
        pass
