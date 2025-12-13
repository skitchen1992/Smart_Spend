"""Фикстуры для тестов модуля groups"""

from typing import AsyncGenerator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.groups.router import router as groups_router
from app.core.db import get_db
from app.core.dependencies import get_current_user


@pytest.fixture
def test_app(mock_db_session, mock_user):
    """Создает тестовое приложение с переопределенными зависимостями"""
    app = FastAPI()
    app.include_router(groups_router)

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield mock_db_session

    async def override_get_current_user():
        return mock_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_app):
    """Тестовый клиент"""
    return TestClient(test_app)
