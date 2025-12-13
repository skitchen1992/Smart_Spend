"""
Инициализация ядра приложения
"""

from sqlalchemy import text

from app.core.db import engine
from app.core.config import settings, Settings


async def init_db() -> None:
    """
    Инициализация базы данных (асинхронная)

    Примечание: Создание таблиц выполняется через Alembic миграции.
    Эта функция проверяет подключение к БД при старте приложения.
    """
    # Проверка подключения к БД
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))


def get_settings() -> Settings:
    """Получение настроек приложения"""
    return settings
