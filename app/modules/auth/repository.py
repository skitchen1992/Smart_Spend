from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import RefreshToken


class RefreshTokenRepository:
    """Работа с refresh токенами"""

    async def create(
        self,
        db: AsyncSession,
        *,
        token_jti: str,
        token_hash: str,
        user_id: int,
        expires_at: datetime,
    ) -> RefreshToken:
        token = RefreshToken(
            token_jti=token_jti,
            token_hash=token_hash,
            user_id=user_id,
            expires_at=expires_at,
        )
        db.add(token)
        await db.flush()
        await db.refresh(token)
        return token

    async def get_by_jti(self, db: AsyncSession, token_jti: str) -> RefreshToken | None:
        result = await db.execute(select(RefreshToken).where(RefreshToken.token_jti == token_jti))
        return result.scalar_one_or_none()

    async def revoke(self, db: AsyncSession, token: RefreshToken) -> RefreshToken:
        token.is_revoked = True
        await db.flush()
        await db.refresh(token)
        return token


refresh_token_repository = RefreshTokenRepository()
