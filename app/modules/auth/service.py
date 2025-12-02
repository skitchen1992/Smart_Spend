from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
    decode_access_token,
    hash_token,
)
from app.modules.users.models import User
from app.modules.users.service import user_service
from app.core.exceptions import CredentialsException
from app.modules.auth.repository import refresh_token_repository


class AuthService:
    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
        user = await user_service.get_user_by_username(db, username)
        if not user:
            user = await user_service.get_user_by_email(db, username)

        if not user or not user.is_active:
            return None

        # Проверяем, что хэш пароля существует и не пустой
        if not user.hashed_password:
            return None

        if not verify_password(password, user.hashed_password):  # type: ignore[arg-type]
            return None

        return user

    @staticmethod
    async def generate_tokens(db: AsyncSession, user: User) -> dict[str, str]:
        if not user.is_active:
            raise CredentialsException(detail="User is inactive")
        if user.id is None:
            raise CredentialsException(detail="User identifier is missing")

        payload: dict[str, Any] = {"sub": user.username}

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data=payload, expires_delta=access_token_expires)

        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        refresh_expiration = datetime.now(timezone.utc) + refresh_token_expires
        refresh_token, token_jti = create_refresh_token(
            data=payload, expires_delta=refresh_token_expires, jti=str(uuid4())
        )

        await refresh_token_repository.create(
            db,
            token_jti=token_jti,
            token_hash=hash_token(refresh_token),
            user_id=user.id,  # type: ignore[arg-type]
            expires_at=refresh_expiration,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    @staticmethod
    async def refresh_access_token(db: AsyncSession, refresh_token: str) -> dict[str, str]:
        payload = decode_access_token(refresh_token)
        if not payload:
            raise CredentialsException(detail="Invalid refresh token")

        if payload.get("type") != "refresh":
            raise CredentialsException(detail="Invalid token type")

        username = payload.get("sub")
        token_jti = payload.get("jti")
        if not username or not token_jti:
            raise CredentialsException(detail="Invalid token payload")

        token_record = await refresh_token_repository.get_by_jti(db, token_jti)
        if not token_record:
            raise CredentialsException(detail="Refresh token not found")

        if token_record.is_revoked:
            raise CredentialsException(detail="Refresh token has been revoked")

        if token_record.expires_at <= datetime.now(timezone.utc):
            raise CredentialsException(detail="Refresh token expired")

        if token_record.token_hash != hash_token(refresh_token):
            raise CredentialsException(detail="Refresh token mismatch")

        user = await user_service.get_user_by_id(db, token_record.user_id)  # type: ignore[arg-type]
        if not user or not user.is_active or user.username != username:
            raise CredentialsException(detail="User not found")

        await refresh_token_repository.revoke(db, token_record)

        return await AuthService.generate_tokens(db, user)

    @staticmethod
    async def get_user_from_token(db: AsyncSession, token: str) -> User:
        payload = decode_access_token(token)
        if not payload:
            raise CredentialsException(detail="Invalid access token")

        if payload.get("type") != "access":
            raise CredentialsException(detail="Unsupported token type")

        username = payload.get("sub")
        if not username:
            raise CredentialsException(detail="Invalid token payload")

        user = await user_service.get_user_by_username(db, username)
        if not user or not user.is_active:
            raise CredentialsException(detail="User not found")

        return user


auth_service = AuthService()
