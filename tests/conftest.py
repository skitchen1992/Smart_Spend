"""Общие фикстуры для тестов"""

from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import User
from app.modules.auth.models import RefreshToken
from app.core.config import settings


@pytest.fixture
def mock_db_session() -> AsyncMock:
    """Мок AsyncSession для БД"""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_user():
    """Фикстура для создания тестового пользователя"""
    # Используем MagicMock для создания мок-объекта без SQLAlchemy инициализации
    user = MagicMock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.full_name = "Test User"
    user.hashed_password = "$argon2id$v=19$m=65536,t=3,p=4$test_hash"
    user.is_active = True
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = None
    return user


@pytest.fixture
def mock_inactive_user():
    """Фикстура для создания неактивного пользователя"""
    # Используем MagicMock для создания мок-объекта без SQLAlchemy инициализации
    user = MagicMock(spec=User)
    user.id = 2
    user.username = "inactive_user"
    user.email = "inactive@example.com"
    user.full_name = "Inactive User"
    user.hashed_password = "$argon2id$v=19$m=65536,t=3,p=4$test_hash"
    user.is_active = False
    user.created_at = datetime.now(timezone.utc)
    user.updated_at = None
    return user


@pytest.fixture
def mock_refresh_token():
    """Фикстура для создания тестового refresh токена"""
    # Используем MagicMock для создания мок-объекта без SQLAlchemy инициализации
    token = MagicMock(spec=RefreshToken)
    token.id = 1
    token.token_jti = "test-jti-123"
    token.token_hash = "test_token_hash"
    token.user_id = 1
    token.expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    token.is_revoked = False
    token.created_at = datetime.now(timezone.utc)
    token.updated_at = None
    return token


@pytest.fixture
def mock_user_service():
    """Мок user_service"""
    from unittest.mock import MagicMock

    service = MagicMock()
    service.get_user_by_id = AsyncMock()
    service.get_user_by_username = AsyncMock()
    service.get_user_by_email = AsyncMock()
    service.create_user = AsyncMock()
    return service


@pytest.fixture
def mock_refresh_token_repository():
    """Мок refresh_token_repository"""
    from unittest.mock import MagicMock

    repository = MagicMock()
    repository.create = AsyncMock()
    repository.get_by_jti = AsyncMock()
    repository.revoke = AsyncMock()
    return repository


@pytest.fixture
def mock_settings(monkeypatch):
    """Мок настроек приложения"""
    monkeypatch.setattr(settings, "SECRET_KEY", "test_secret_key_32_chars_long!")
    monkeypatch.setattr(settings, "ALGORITHM", "HS256")
    monkeypatch.setattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 30)
    monkeypatch.setattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS", 7)
    return settings
