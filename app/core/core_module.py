"""
Инициализация ядра приложения
Здесь можно добавить логику инициализации БД, миграций и т.д.
"""
from app.core.db import engine, Base
from app.core.config import settings


def init_db():
    """Инициализация базы данных"""
    # Создание всех таблиц
    Base.metadata.create_all(bind=engine)


def get_settings():
    """Получение настроек приложения"""
    return settings

