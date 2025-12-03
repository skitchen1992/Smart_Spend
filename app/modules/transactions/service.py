# app/modules/transactions/service.py

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.transactions.models import Transaction
from app.modules.transactions.repository import transaction_repository
from app.modules.transactions.schemas import (
    TransactionCreate,
    TransactionUpdate,
    TransactionFilters,
    PaginationParams,
    PaginatedTransactionResponse,
    TransactionResponse,
)


class TransactionService:
    """Сервис для работы с транзакциями"""

    async def create_transaction(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        transaction_in: TransactionCreate,
    ) -> Transaction:
        return await transaction_repository.create(
            db=db,
            obj_in=transaction_in,
            user_id=user_id,
        )

    async def get_transaction(
        self,
        db: AsyncSession,
        *,
        transaction_id: int,
        user_id: int,
    ) -> Transaction | None:
        return await transaction_repository.get(
            db=db,
            transaction_id=transaction_id,
            user_id=user_id,
        )

    async def list_transactions(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        category: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> PaginatedTransactionResponse:
        """Получить список транзакций с фильтрами и пагинацией"""
        # Создаем объект фильтров из параметров
        filters = None
        if category or date_from or date_to:
            date_from_parsed = None
            date_to_parsed = None
            if date_from:
                try:
                    date_from_parsed = datetime.strptime(date_from, "%Y-%m-%d").date()
                except ValueError:
                    pass  # Игнорируем неверный формат даты
            if date_to:
                try:
                    date_to_parsed = datetime.strptime(date_to, "%Y-%m-%d").date()
                except ValueError:
                    pass  # Игнорируем неверный формат даты
            filters = TransactionFilters(
                category=category,
                date_from=date_from_parsed,
                date_to=date_to_parsed,
            )

        # Создаем объект пагинации
        pagination = PaginationParams(page=page, page_size=page_size)

        skip = (pagination.page - 1) * pagination.page_size

        # Получаем транзакции и общее количество
        transactions = await transaction_repository.list(
            db=db,
            user_id=user_id,
            filters=filters,
            skip=skip,
            limit=pagination.page_size,
        )

        total = await transaction_repository.count(
            db=db,
            user_id=user_id,
            filters=filters,
        )

        # Вычисляем общее количество страниц
        pages = (total + pagination.page_size - 1) // pagination.page_size if total > 0 else 0

        # Преобразуем Transaction объекты в TransactionResponse
        items = [TransactionResponse.model_validate(tx) for tx in transactions]

        return PaginatedTransactionResponse(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            pages=pages,
        )

    async def update_transaction(
        self,
        db: AsyncSession,
        *,
        db_obj: Transaction,
        transaction_in: TransactionUpdate,
    ) -> Transaction:
        return await transaction_repository.update(
            db=db,
            db_obj=db_obj,
            obj_in=transaction_in,
        )

    async def delete_transaction(
        self,
        db: AsyncSession,
        *,
        db_obj: Transaction,
    ) -> None:
        await transaction_repository.delete(db=db, db_obj=db_obj)


transaction_service = TransactionService()
