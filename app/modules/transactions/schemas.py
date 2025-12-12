from datetime import datetime, date
from typing import Optional, List

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
    transaction_to_group: int = Field(
        None,
        description="Отношение к группе"
    )


class TransactionCreate(TransactionBase):
    """Схема для создания транзакции"""


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


class TransactionFilters(BaseModel):
    """Схема фильтров для списка транзакций"""

    category: Optional[str] = Field(
        None,
        description="Фильтр по категории транзакции",
    )
    date_from: Optional[date] = Field(
        None,
        description="Начальная дата для фильтрации (включительно)",
    )
    date_to: Optional[date] = Field(
        None,
        description="Конечная дата для фильтрации (включительно)",
    )


class PaginationParams(BaseModel):
    """Параметры пагинации"""

    page: int = Field(
        default=1,
        ge=1,
        description="Номер страницы (начинается с 1)",
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Количество элементов на странице (максимум 100)",
    )


class PaginatedTransactionResponse(BaseModel):
    """Схема ответа с пагинированным списком транзакций"""

    items: List[TransactionResponse] = Field(description="Список транзакций")
    total: int = Field(description="Общее количество транзакций")
    page: int = Field(description="Текущая страница")
    page_size: int = Field(description="Размер страницы")
    pages: int = Field(description="Общее количество страниц")

    class Config:
        from_attributes = True
