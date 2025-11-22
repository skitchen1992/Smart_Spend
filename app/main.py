from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.core_module import init_db
from app.core.db import engine
from app.core.exceptions import AppException
from app.core.exceptions_handler import app_exception_handler, http_exception_handler
from app.core.middleware import StandardResponseMiddleware
from app.modules.users.router import router as users_router
from app.modules.groups.router import router as groups_router
from app.modules.analytics.router import router as analytics_router
from app.modules.group_members.router import router as group_members_router

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Инициализация при старте приложения"""
    # Инициализация БД
    try:
        await init_db()
    except Exception as e:
        # Логируем ошибку, но не падаем при старте
        # БД может быть недоступна при первом запуске
        import logging

        logging.warning(f"Не удалось инициализировать БД при старте: {e}")
    yield
    # Очистка при завершении
    await engine.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API для управления расходами",
    version=settings.VERSION,
    lifespan=lifespan,
)

# Middleware для стандартизированного формата ответов (добавляем первым, чтобы выполнялся последним)
app.add_middleware(StandardResponseMiddleware)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрация обработчиков исключений
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

# Подключение роутов модулей
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(groups_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)
app.include_router(group_members_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Welcome to Smart Spend API"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
