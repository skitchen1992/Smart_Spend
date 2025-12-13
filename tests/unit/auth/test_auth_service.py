"""Тесты для app/modules/auth/service.py"""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from app.modules.auth.service import AuthService
from app.core.exceptions import CredentialsException
from app.core.security import get_password_hash, create_access_token, create_refresh_token


class TestAuthenticateUser:
    """Тесты для authenticate_user"""

    @pytest.mark.asyncio
    async def test_authenticate_user_by_username_success(
        self, mock_db_session: AsyncMock, mock_user: MagicMock
    ) -> None:
        """Успешная аутентификация по username"""
        password = "test_password_123"
        mock_user.hashed_password = get_password_hash(password)

        with patch("app.modules.auth.service.user_service") as mock_user_service:
            mock_user_service.get_user_by_username = AsyncMock(return_value=mock_user)
            mock_user_service.get_user_by_email = AsyncMock(return_value=None)

            result = await AuthService.authenticate_user(
                mock_db_session, mock_user.username, password
            )

            assert result is not None
            assert result.id == mock_user.id
            assert result.username == mock_user.username
            mock_user_service.get_user_by_username.assert_called_once_with(
                mock_db_session, mock_user.username
            )

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(
        self, mock_db_session: AsyncMock, mock_user: MagicMock
    ) -> None:
        """Аутентификация с неверным паролем"""
        password = "test_password_123"
        wrong_password = "wrong_password"
        mock_user.hashed_password = get_password_hash(password)

        with patch("app.modules.auth.service.user_service") as mock_user_service:
            mock_user_service.get_user_by_username = AsyncMock(return_value=mock_user)
            mock_user_service.get_user_by_email = AsyncMock(return_value=None)

            result = await AuthService.authenticate_user(
                mock_db_session, mock_user.username, wrong_password
            )

            assert result is None


class TestGenerateTokens:
    """Тесты для generate_tokens"""

    @pytest.mark.asyncio
    async def test_generate_tokens_success(
        self, mock_db_session: AsyncMock, mock_user: MagicMock
    ) -> None:
        """Успешная генерация токенов"""
        mock_user.id = 1
        mock_user.is_active = True

        with patch("app.modules.auth.service.refresh_token_repository") as mock_repo:
            mock_token_record = MagicMock()
            mock_repo.create = AsyncMock(return_value=mock_token_record)

            result = await AuthService.generate_tokens(mock_db_session, mock_user)

            assert "access_token" in result
            assert "refresh_token" in result
            assert isinstance(result["access_token"], str)
            assert isinstance(result["refresh_token"], str)
            assert len(result["access_token"]) > 0
            assert len(result["refresh_token"]) > 0
            mock_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_tokens_inactive_user(
        self, mock_db_session: AsyncMock, mock_inactive_user: MagicMock
    ) -> None:
        """Генерация токенов для неактивного пользователя"""
        mock_inactive_user.id = 2
        mock_inactive_user.is_active = False

        with pytest.raises(CredentialsException) as exc_info:
            await AuthService.generate_tokens(mock_db_session, mock_inactive_user)

        assert "неактивен" in exc_info.value.detail.lower()


class TestRefreshAccessToken:
    """Тесты для refresh_access_token"""

    @pytest.mark.asyncio
    async def test_refresh_access_token_success(
        self,
        mock_db_session: AsyncMock,
        mock_user: MagicMock,
        mock_refresh_token: MagicMock,
    ) -> None:
        """Успешное обновление токенов"""
        mock_user.id = 1
        mock_user.is_active = True

        payload = {"sub": mock_user.username}
        refresh_token, token_jti = create_refresh_token(payload)
        from app.core.security import hash_token

        token_hash = hash_token(refresh_token)

        mock_refresh_token.token_jti = token_jti
        mock_refresh_token.token_hash = token_hash
        mock_refresh_token.user_id = mock_user.id
        mock_refresh_token.is_revoked = False
        mock_refresh_token.expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        with (
            patch("app.modules.auth.service.refresh_token_repository") as mock_repo,
            patch("app.modules.auth.service.user_service") as mock_user_service,
        ):
            mock_repo.get_by_jti = AsyncMock(return_value=mock_refresh_token)
            mock_repo.revoke = AsyncMock(return_value=mock_refresh_token)
            mock_repo.create = AsyncMock(return_value=mock_refresh_token)
            mock_user_service.get_user_by_id = AsyncMock(return_value=mock_user)

            result = await AuthService.refresh_access_token(mock_db_session, refresh_token)

            assert "access_token" in result
            assert "refresh_token" in result
            mock_repo.get_by_jti.assert_called_once()
            mock_repo.revoke.assert_called_once()

    @pytest.mark.asyncio
    async def test_refresh_access_token_invalid_token(self, mock_db_session: AsyncMock) -> None:
        """Обновление токенов с невалидным токеном"""
        invalid_token = "invalid.token.here"

        with pytest.raises(CredentialsException) as exc_info:
            await AuthService.refresh_access_token(mock_db_session, invalid_token)

        assert "недействительный" in exc_info.value.detail.lower()


class TestGetUserFromToken:
    """Тесты для get_user_from_token"""

    @pytest.mark.asyncio
    async def test_get_user_from_token_success(
        self, mock_db_session: AsyncMock, mock_user: MagicMock
    ) -> None:
        """Успешное получение пользователя из токена"""
        payload = {"sub": mock_user.username}
        access_token = create_access_token(payload)

        with patch("app.modules.auth.service.user_service") as mock_user_service:
            mock_user_service.get_user_by_username = AsyncMock(return_value=mock_user)

            result = await AuthService.get_user_from_token(mock_db_session, access_token)

            assert result is not None
            assert result.id == mock_user.id
            assert result.username == mock_user.username
            mock_user_service.get_user_by_username.assert_called_once_with(
                mock_db_session, mock_user.username
            )

    @pytest.mark.asyncio
    async def test_get_user_from_token_invalid_token(self, mock_db_session: AsyncMock) -> None:
        """Получение пользователя из невалидного токена"""
        invalid_token = "invalid.token.here"

        with pytest.raises(CredentialsException) as exc_info:
            await AuthService.get_user_from_token(mock_db_session, invalid_token)

        assert "недействительный" in exc_info.value.detail.lower()
