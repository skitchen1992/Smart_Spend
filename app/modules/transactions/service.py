# app/modules/transactions/service.py

from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.transactions.models import Transaction
from app.modules.transactions.repository import transaction_repository
from app.modules.transactions.schemas import TransactionCreate, TransactionUpdate


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
    ) -> Sequence[Transaction]:
        return await transaction_repository.list(
            db=db,
            user_id=user_id,
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
