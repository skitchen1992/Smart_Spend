from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.db import get_db

# Базовые зависимости можно расширять здесь
# Например, для получения текущего пользователя из токена

def get_database() -> Session:
    """Получение сессии БД"""
    return next(get_db())

