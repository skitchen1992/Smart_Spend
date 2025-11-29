from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.modules.transactions.models import TransactionType


class TransactionBase(BaseModel):
    """Базовая схема транзакции"""

    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Название транзакции",
    )
    amount: float = Field(
        ...,
        gt=0,
        description="Сумма транзакции",
    )
    description: Optional[str] = Field(
        None,
        description="Описание транзакции",
    )
    category: Optional[str] = Field(
        None,
        max_length=50,
        description="Категория транзакции",
    )
    type: TransactionType = Field(
        default=TransactionType.EXPENSE,
        description="Тип транзакции (доход/расход)",
    )


class TransactionCreate(TransactionBase):
    """Схема для создания транзакции"""
    user_id: int = Field(
        ...,
        gt=0,
        description="ID пользователя-владельца транзакции",
    )


class TransactionUpdate(BaseModel):
    """Схема для обновления транзакции"""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    amount: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=50)
    type: Optional[TransactionType] = None


class TransactionResponse(TransactionBase):
    """Схема ответа с транзакцией"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Для работы с ORM-объектами
