from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field
from typing import List, Union, Any
import json


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )

    # Основные настройки
    PROJECT_NAME: str = "Smart Spend"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # Параметры PostgreSQL (для Docker Compose)
    POSTGRES_USER: str = Field(default="", description="Имя пользователя PostgreSQL")
    POSTGRES_PASSWORD: str = Field(default="", description="Пароль пользователя PostgreSQL")
    POSTGRES_DB: str = Field(default="", description="Имя базы данных PostgreSQL")

    # База данных (ОБЯЗАТЕЛЬНО установите через переменную окружения!)
    DATABASE_URL: str = Field(
        default="",
        description="URL подключения к базе данных. Должно быть установлено через DATABASE_URL в .env",
    )

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Проверка что DATABASE_URL установлен"""
        if not v or v.strip() == "":
            raise ValueError(
                "DATABASE_URL не установлен! Пожалуйста, установите переменную окружения DATABASE_URL "
                "или создайте файл .env на основе .env.example"
            )
        return v

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:8000"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        """Парсинг CORS_ORIGINS из строки или списка"""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # Если строка начинается с [, пытаемся распарсить как JSON
            v_stripped = v.strip()
            if v_stripped.startswith("["):
                try:
                    parsed = json.loads(v_stripped)
                    if isinstance(parsed, list):
                        return parsed
                except (json.JSONDecodeError, ValueError):
                    pass
            # Иначе разбиваем по запятой
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        # Если уже список, возвращаем как есть
        if isinstance(v, (list, tuple)):
            return list(v)
        # Fallback на значение по умолчанию
        return ["http://localhost:3000", "http://localhost:8000"]

    # Безопасность (ОБЯЗАТЕЛЬНО установите через переменную окружения!)
    SECRET_KEY: str = Field(
        default="",
        description="Секретный ключ для JWT токенов. Должно быть установлено через SECRET_KEY в .env",
    )

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Проверка что SECRET_KEY установлен"""
        if not v or v.strip() == "":
            raise ValueError(
                "SECRET_KEY не установлен! Пожалуйста, установите переменную окружения SECRET_KEY "
                "или создайте файл .env на основе .env.example"
            )
        if len(v) < 32:
            raise ValueError("SECRET_KEY должен быть не менее 32 символов для безопасности!")
        return v

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()
