from typing import Optional
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from services.auth.app.data.repositories.interfaces.i_user_repository import IUserRepository
from services.auth.app.domain.models.db import User
from services.auth.app.domain.models.enums.user_roles import UserRole


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
        user = User(email=email, role=role)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_role(self, user_id: UUID | str, new_role: UserRole) -> None:
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(role=new_role)
        )
        await self.session.commit()

    async def deactivate(self, user_id: UUID | str) -> None:
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=False)
        )
        await self.session.commit()
