# app/modules/transactions/repository.py

from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.transactions.models import Transaction
from app.modules.transactions.schemas import TransactionCreate, TransactionUpdate


class TransactionRepository:
    """Репозиторий для работы с транзакциями"""

    async def create(
        self,
        db: AsyncSession,
        *,
        obj_in: TransactionCreate,
    ) -> Transaction:
        data = obj_in.model_dump()
        db_obj = Transaction(**data)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def get(
        self,
        db: AsyncSession,
        transaction_id: int,
    ) -> Transaction | None:
        result = await db.execute(
            select(Transaction).where(Transaction.id == transaction_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
    ) -> Sequence[Transaction]:
        result = await db.execute(select(Transaction))
        return result.scalars().all()

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: Transaction,
        obj_in: TransactionUpdate,
    ) -> Transaction:
        data = obj_in.model_dump(exclude_unset=True, exclude_none=True)
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


transaction_repository = TransactionRepository()
