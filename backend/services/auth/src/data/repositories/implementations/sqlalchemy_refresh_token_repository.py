from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from libs.common.utils.crypto import hash_value
from services.auth.src.domain.models.db import RefreshToken


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, user_id: UUID, raw_token: str, jti: str, expires_at: datetime) -> None:
        refresh = RefreshToken(
            user_id=user_id,
            jti=jti,
            token_hash=hash_value(raw_token),
            expires_at=expires_at,
        )
        self.session.add(refresh)

    async def find_active_by_jti(self, jti: str) -> RefreshToken | None:
        result = await self.session.execute(
            select(RefreshToken)
            .where(RefreshToken.jti == jti)
            .where(RefreshToken.revoked_at.is_(None))
            .where(RefreshToken.expires_at > datetime.now(timezone.utc))
        )
        return result.scalar_one_or_none()

    async def revoke_by_jti(self, jti: str) -> None:
        await self.session.execute(
            update(RefreshToken)
            .where(RefreshToken.jti == jti)
            .values(revoked_at=datetime.now(timezone.utc))
        )
