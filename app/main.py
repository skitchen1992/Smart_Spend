from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.core_module import init_db
from app.modules.transactions.router import router as transactions_router
from app.modules.users.router import router as users_router
from app.modules.groups.router import router as groups_router
from app.modules.analytics.router import router as analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация при старте приложения"""
    # Инициализация БД
    init_db()
    yield
    # Очистка при завершении (если нужно)


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API для управления расходами",
    version=settings.VERSION,
    lifespan=lifespan,
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутов модулей
app.include_router(transactions_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)
app.include_router(groups_router, prefix=settings.API_V1_STR)
app.include_router(analytics_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "Welcome to Smart Spend API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
