"""Фикстуры для тестов модуля transactions"""

from typing import AsyncGenerator, Any

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.modules.transactions.router import router
from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import AppException
from app.core.exceptions_handler import (
    app_exception_handler,
    http_exception_handler,
    sqlalchemy_error_handler,
)


@pytest.fixture
def test_app(mock_db_session: Any, mock_user: Any) -> Any:
    """Создает тестовое приложение с переопределенными зависимостями"""
    app = FastAPI()
    app.include_router(router)

    # Регистрация обработчиков исключений (как в main.py)
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)

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
