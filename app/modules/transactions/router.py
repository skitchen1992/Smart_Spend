# app/modules/transactions/router.py

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.dto.response import StandardResponse, success_response
from app.core.exceptions import NotFoundException
from app.modules.transactions.schemas import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
)
from app.modules.transactions.service import transaction_service

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post(
    "",
    response_model=StandardResponse[TransactionResponse],
    status_code=201,
)
async def create_transaction(
    transaction_in: TransactionCreate,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[TransactionResponse]:
    """Создать транзакцию"""
    tx = await transaction_service.create_transaction(db=db, transaction_in=transaction_in)
    data = TransactionResponse.model_validate(tx)
    return success_response(data=data, code=201)


@router.get(
    "",
    response_model=StandardResponse[List[TransactionResponse]],
)
async def list_transactions(
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[List[TransactionResponse]]:
    """Получить список всех транзакций"""
    txs = await transaction_service.list_transactions(db=db)
    data = [TransactionResponse.model_validate(tx) for tx in txs]
    return success_response(data=data)


@router.get(
    "/{transaction_id}",
    response_model=StandardResponse[TransactionResponse],
)
async def get_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[TransactionResponse]:
    """Получить транзакцию по id"""
    tx = await transaction_service.get_transaction(db=db, transaction_id=transaction_id)
    if not tx:
        raise NotFoundException(detail="Транзакция не найдена")

    data = TransactionResponse.model_validate(tx)
    return success_response(data=data)


@router.put(
    "/{transaction_id}",
    response_model=StandardResponse[TransactionResponse],
)
async def update_transaction(
    transaction_id: int,
    transaction_in: TransactionUpdate,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[TransactionResponse]:
    """Обновить транзакцию по id"""
    tx = await transaction_service.get_transaction(db=db, transaction_id=transaction_id)
    if not tx:
        raise NotFoundException(detail="Транзакция не найдена")

    tx = await transaction_service.update_transaction(
        db=db,
        db_obj=tx,
        transaction_in=transaction_in,
    )
    data = TransactionResponse.model_validate(tx)
    return success_response(data=data)


@router.delete(
    "/{transaction_id}",
    response_model=StandardResponse[dict],
)
async def delete_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[dict]:
    """Удалить транзакцию по id"""
    tx = await transaction_service.get_transaction(db=db, transaction_id=transaction_id)
    if not tx:
        raise NotFoundException(detail="Транзакция не найдена")

    await transaction_service.delete_transaction(db=db, db_obj=tx)
    return success_response(data={"message": "Транзакция удалена"})
