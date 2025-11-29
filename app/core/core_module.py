"""
Инициализация ядра приложения
Здесь можно добавить логику инициализации БД, миграций и т.д.
"""

from app.core.db import engine, Base
from app.core.config import settings, Settings


async def init_db() -> None:
    """Инициализация базы данных (асинхронная)"""
    # Создание всех таблиц
    async with engine.begin() as conn:
        pass
        # await conn.run_sync(Base.metadata.create_all)


def get_settings() -> Settings:
    """Получение настроек приложения"""
    return settings
