"""Фикстуры для тестов модуля analytics"""

from typing import AsyncGenerator, Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.router import router
from app.core.db import get_db
from app.core.dependencies import get_current_user


@pytest.fixture
def test_app(mock_db_session: Any, mock_user: Any) -> Any:
    """Создает тестовое приложение с переопределенными зависимостями"""
    app = FastAPI()
    app.include_router(router)

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield mock_db_session

    async def override_get_current_user() -> Any:
        return mock_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_app: Any) -> TestClient:
    """Тестовый клиент"""
    return TestClient(test_app)
