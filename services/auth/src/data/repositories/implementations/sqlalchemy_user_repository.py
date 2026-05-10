from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from data.repositories.interfaces.i_user_repository import IUserRepository
from domain.models.db import User
from domain.models.db.user_role import UserRoleRecord
from domain.models.enums.user_roles import UserRole


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID | str) -> Optional[User]:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def create(self, email: str, role: UserRole = UserRole.USER) -> User:
        user = User(email=email)
        self.session.add(user)
        await self.session.flush()

        role_record = UserRoleRecord(user_id=user.id, role=role.value)
        self.session.add(role_record)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_effective_role(self, user_id: UUID | str) -> str:
        """Возвращает роль из user_roles, при отсутствии — возвращает USER по умолчанию."""
        result = await self.session.execute(
            select(UserRoleRecord).where(UserRoleRecord.user_id == user_id)
        )
        record = result.scalar_one_or_none()
        if record:
            return record.role
        return UserRole.USER.value

    async def update_role(self, user_id: UUID | str, new_role: UserRole) -> None:
        result = await self.session.execute(
            select(UserRoleRecord).where(UserRoleRecord.user_id == user_id)
        )
        record = result.scalar_one_or_none()
        if record:
            await self.session.execute(
                update(UserRoleRecord)
                .where(UserRoleRecord.user_id == user_id)
                .values(role=new_role.value)
            )
        else:
            self.session.add(UserRoleRecord(user_id=user_id, role=new_role.value))
        await self.session.commit()

    async def get_all(self) -> list[tuple[User, str]]:
        """Возвращает список (User, effective_role)."""
        users_result = await self.session.execute(select(User))
        users = users_result.scalars().all()

        roles_result = await self.session.execute(select(UserRoleRecord))
        roles_map = {r.user_id: r.role for r in roles_result.scalars().all()}

        result = []
        for user in users:
            role = roles_map.get(user.id, UserRole.USER.value)
            result.append((user, role))
        return result

    async def deactivate(self, user_id: UUID | str) -> None:
        await self.session.execute(
            update(User).where(User.id == user_id).values(is_active=False)
        )
        await self.session.commit()
