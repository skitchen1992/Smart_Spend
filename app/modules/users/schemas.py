# Pydantic-схемы (DTO) для пользователей
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Базовая схема пользователя"""

    username: str = Field(..., min_length=3, max_length=50, description="Имя пользователя")
    email: EmailStr = Field(..., description="Email пользователя")
    full_name: str | None = Field(None, max_length=200, description="Полное имя")


class UserResponse(UserBase):
    """Схема для ответа API (без пароля)"""

    id: int
    is_active: bool = Field(True, description="Активен ли пользователь")
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True  # Для Pydantic v2 (ранее orm_mode)


class UserCreate(UserBase):
    """Схема для создания пользователя"""

    password: str = Field(..., min_length=8, description="Пароль пользователя")
