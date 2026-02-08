from abc import ABC, abstractmethod
from uuid import UUID

from domain.models.db import User
from domain.models.enums.user_roles import UserRole


class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID | str) -> User | None:
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        pass

    @abstractmethod
    async def create(self, email: str, role: UserRole = UserRole.USER) -> User:
        pass

    @abstractmethod
    async def update_role(self, user_id: UUID | str, new_role: UserRole) -> None:
        pass

    @abstractmethod
    async def deactivate(self, user_id: UUID | str) -> None:
        pass
