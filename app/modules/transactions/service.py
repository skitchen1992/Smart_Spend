# app/modules/transactions/service.py

import csv
import io
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.groups.repository import group_repository
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
        # Проверяем, указана ли группа
        if transaction_in.transaction_to_group:
            # Проверяем, состоит ли пользователь в указанной группе
            group = await group_repository.get_group(
                db=db,
                group_id=transaction_in.transaction_to_group,
                id_user=user_id
            )

            if not group:
                raise HTTPException(
                    status_code=403,
                    detail=f"User is not a member of group {transaction_in.transaction_to_group} or group does not exist"
                )
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
        # Проверяем, изменяется ли группа
        if transaction_in.transaction_to_group is not None:
            # Если группа меняется, проверяем доступ к новой группе
            user_id = db_obj.user_id  # Получаем ID пользователя из существующей транзакции

            if transaction_in.transaction_to_group:
                group = await group_repository.get_group(
                    db=db,
                    group_id=transaction_in.transaction_to_group,
                    id_user=user_id
                )

                if not group:
                    raise HTTPException(
                        status_code=403,
                        detail=f"User is not a member of group {transaction_in.transaction_to_group}"
                    )
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

    async def export_transactions_to_csv(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        category: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> str:
        """Экспортировать транзакции в CSV формат"""
        filters = None
        if category or date_from or date_to:
            date_from_parsed = None
            date_to_parsed = None
            if date_from:
                try:
                    date_from_parsed = datetime.strptime(date_from, "%Y-%m-%d").date()
                except ValueError:
                    pass
            if date_to:
                try:
                    date_to_parsed = datetime.strptime(date_to, "%Y-%m-%d").date()
                except ValueError:
                    pass
            filters = TransactionFilters(
                category=category,
                date_from=date_from_parsed,
                date_to=date_to_parsed,
            )

        transactions = await transaction_repository.list_all(
            db=db,
            user_id=user_id,
            filters=filters,
        )

        output = io.StringIO()
        writer = csv.writer(output, delimiter=",", quoting=csv.QUOTE_MINIMAL)

        writer.writerow(
            [
                "ID",
                "Название",
                "Сумма",
                "Тип",
                "Категория",
                "Описание",
                "Дата создания",
                "Дата обновления",
                "Группа ID",
            ]
        )

        for tx in transactions:
            writer.writerow(
                [
                    tx.id,
                    tx.title,
                    tx.amount,
                    tx.type.value,
                    tx.category or "",
                    tx.description or "",
                    tx.created_at.strftime("%Y-%m-%d %H:%M:%S") if tx.created_at else "",
                    tx.updated_at.strftime("%Y-%m-%d %H:%M:%S") if tx.updated_at else "",
                    tx.transaction_to_group or "",  # Добавляем ID группы
                ]
            )

        csv_content = output.getvalue()
        output.close()

        return "\ufeff" + csv_content


transaction_service = TransactionService()
