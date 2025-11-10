from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
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
    
    # База данных
    DATABASE_URL: str = "sqlite:///./smart_spend.db"
    
    # CORS
    CORS_ORIGINS: Union[str, List[str]] = "http://localhost:3000,http://localhost:8000"
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v: Any) -> List[str]:
        """Парсинг CORS_ORIGINS из строки или списка"""
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            # Если строка начинается с [, пытаемся распарсить как JSON
            v_stripped = v.strip()
            if v_stripped.startswith('['):
                try:
                    parsed = json.loads(v_stripped)
                    if isinstance(parsed, list):
                        return parsed
                except (json.JSONDecodeError, ValueError):
                    pass
            # Иначе разбиваем по запятой
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        # Если уже список, возвращаем как есть
        if isinstance(v, (list, tuple)):
            return list(v)
        # Fallback на значение по умолчанию
        return ["http://localhost:3000", "http://localhost:8000"]
    
    # Безопасность
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()

