from abc import ABC, abstractmethod
from typing import Optional


class OTPRepository(ABC):
    @abstractmethod
    async def save(self, email: str, otp_hash: str, ttl: int) -> None:
        pass

    @abstractmethod
    async def get(self, email: str) -> Optional[str]:
        pass

    @abstractmethod
    async def delete(self, email: str) -> None:
        pass
