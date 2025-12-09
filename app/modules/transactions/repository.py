# app/modules/transactions/repository.py

from typing import Sequence, Dict
from datetime import datetime, time

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.transactions.models import Transaction, TransactionType
from app.modules.transactions.schemas import (
    TransactionCreate,
    TransactionUpdate,
    TransactionFilters,
)


class TransactionRepository:
    """Репозиторий для работы с транзакциями"""

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: TransactionCreate,
        user_id: int,
    ) -> Transaction:
        data = obj_in.model_dump()
        data["user_id"] = user_id
        db_obj = Transaction(**data)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def get(
        self,
        db: AsyncSession,
        *,
        transaction_id: int,
        user_id: int,
    ) -> Transaction | None:
        result = await db.execute(
            select(Transaction).where(
                Transaction.id == transaction_id,
                Transaction.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        filters: TransactionFilters | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> Sequence[Transaction]:
        """Получить список транзакций с фильтрами и пагинацией"""
        query = select(Transaction).where(Transaction.user_id == user_id)

        # Применяем фильтры
        if filters:
            conditions = []

            if filters.category:
                conditions.append(Transaction.category == filters.category)

            if filters.date_from:
                # Преобразуем date в datetime для сравнения (начало дня)
                date_from_dt = datetime.combine(filters.date_from, time.min)
                conditions.append(Transaction.created_at >= date_from_dt)

            if filters.date_to:
                # Преобразуем date в datetime для сравнения (конец дня)
                date_to_dt = datetime.combine(filters.date_to, time.max)
                conditions.append(Transaction.created_at <= date_to_dt)

            if conditions:
                query = query.where(and_(*conditions))

        # Применяем пагинацию и сортировку
        query = query.order_by(Transaction.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        return result.scalars().all()

    async def count(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        filters: TransactionFilters | None = None,
    ) -> int:
        """Подсчитать общее количество транзакций с фильтрами"""
        query = select(func.count(Transaction.id)).where(Transaction.user_id == user_id)

        # Применяем те же фильтры
        if filters:
            conditions = []

            if filters.category:
                conditions.append(Transaction.category == filters.category)

            if filters.date_from:
                date_from_dt = datetime.combine(filters.date_from, time.min)
                conditions.append(Transaction.created_at >= date_from_dt)

            if filters.date_to:
                date_to_dt = datetime.combine(filters.date_to, time.max)
                conditions.append(Transaction.created_at <= date_to_dt)

            if conditions:
                query = query.where(and_(*conditions))

        result = await db.execute(query)
        return result.scalar_one() or 0

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: Transaction,
        obj_in: TransactionUpdate,
    ) -> Transaction:
        data = obj_in.model_dump(exclude_unset=True, exclude_none=True)
        data.pop("user_id", None)

        for field, value in data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(
        self,
        db: AsyncSession,
        *,
        db_obj: Transaction,
    ) -> None:
        await db.delete(db_obj)
        await db.flush()

    async def get_income_sum(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        date_from: datetime,
        date_to: datetime,
    ) -> float:
        """Получить сумму доходов за период"""
        query = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.INCOME,
            Transaction.created_at >= date_from,
            Transaction.created_at <= date_to,
        )
        result = await db.execute(query)
        return float(result.scalar_one() or 0.0)

    async def get_expense_sum(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        date_from: datetime,
        date_to: datetime,
    ) -> float:
        """Получить сумму расходов за период"""
        query = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.user_id == user_id,
            Transaction.type == TransactionType.EXPENSE,
            Transaction.created_at >= date_from,
            Transaction.created_at <= date_to,
        )
        result = await db.execute(query)
        return float(result.scalar_one() or 0.0)

    async def get_expenses_by_category(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        date_from: datetime,
        date_to: datetime,
    ) -> Dict[str, float]:
        """Получить расходы по категориям за период"""
        query = (
            select(
                Transaction.category,
                func.sum(Transaction.amount).label("total"),
            )
            .where(
                Transaction.user_id == user_id,
                Transaction.type == TransactionType.EXPENSE,
                Transaction.created_at >= date_from,
                Transaction.created_at <= date_to,
                Transaction.category.isnot(None),
            )
            .group_by(Transaction.category)
        )
        result = await db.execute(query)
        rows = result.all()
        return {row.category: float(row.total) for row in rows if row.category}


transaction_repository = TransactionRepository()
