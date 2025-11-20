# Pydantic-схемы (DTO) для пользователей
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Базовая схема пользователя"""

    username: str = Field(..., min_length=3, max_length=50, description="Имя пользователя")
    email: EmailStr = Field(..., description="Email пользователя")
    full_name: str | None = Field(None, max_length=200, description="Полное имя")
    is_active: bool = Field(True, description="Активен ли пользователь")


class UserResponse(UserBase):
    """Схема для ответа API (без пароля)"""

    id: int
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True  # Для Pydantic v2 (ранее orm_mode)
