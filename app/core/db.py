from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

from app.core.config import settings


def get_async_database_url(database_url: str) -> str:
    """Преобразует синхронный PostgreSQL URL в асинхронный"""
    # Если уже асинхронный - возвращаем как есть
    if "+asyncpg" in database_url:
        return database_url

    # PostgreSQL - заменяем на asyncpg
    if database_url.startswith("postgresql+psycopg2://"):
        return database_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # Если формат не распознан - возвращаем как есть
    return database_url


# Создаем async engine
async_database_url = get_async_database_url(settings.DATABASE_URL)

engine = create_async_engine(
    async_database_url,
    echo=True,  # Для разработки - показывает SQL запросы
    pool_pre_ping=True,  # Проверка соединения перед использованием (рекомендуется для PostgreSQL)
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency для получения async сессии БД"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
