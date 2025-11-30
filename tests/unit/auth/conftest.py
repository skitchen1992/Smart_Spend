"""Фикстуры для тестов модуля auth"""

from typing import AsyncGenerator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.router import router
from app.core.db import get_db


@pytest.fixture
def test_app(mock_db_session):
    """Создает тестовое приложение с переопределенными зависимостями"""
    app = FastAPI()
    app.include_router(router)

    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield mock_db_session

    app.dependency_overrides[get_db] = override_get_db
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_app):
    """Тестовый клиент"""
    return TestClient(test_app)

