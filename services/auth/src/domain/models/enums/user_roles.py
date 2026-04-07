from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

    @property
    def is_privileged(self) -> bool:
        return self in (UserRole.ADMIN, UserRole.MANAGER)
