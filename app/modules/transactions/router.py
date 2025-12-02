# app/modules/transactions/router.py

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.dto.response import StandardResponse, success_response
from app.core.exceptions import NotFoundException
from app.core.dependencies import get_current_user
from app.modules.users.models import User
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
    current_user: User = Depends(get_current_user),
) -> StandardResponse[TransactionResponse]:
    """Создать транзакцию текущего пользователя"""
    tx = await transaction_service.create_transaction(
        db=db,
        user_id=current_user.id,
        transaction_in=transaction_in,
    )
    data = TransactionResponse.model_validate(tx)
    return success_response(data=data, code=201)


@router.get(
    "",
    response_model=StandardResponse[List[TransactionResponse]],
)
async def list_transactions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StandardResponse[List[TransactionResponse]]:
    """Получить список всех транзакций текущего пользователя"""
    txs = await transaction_service.list_transactions(
        db=db,
        user_id=current_user.id,
    )
    data = [TransactionResponse.model_validate(tx) for tx in txs]
    return success_response(data=data)


@router.get(
    "/{transaction_id}",
    response_model=StandardResponse[TransactionResponse],
)
async def get_transaction(
    transaction_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StandardResponse[TransactionResponse]:
    """Получить транзакцию по id (только свою)"""
    tx = await transaction_service.get_transaction(
        db=db,
        transaction_id=transaction_id,
        user_id=current_user.id,
    )
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
    current_user: User = Depends(get_current_user),
) -> StandardResponse[TransactionResponse]:
    """Обновить транзакцию по id (только свою)"""
    tx = await transaction_service.get_transaction(
        db=db,
        transaction_id=transaction_id,
        user_id=current_user.id,
    )
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
    current_user: User = Depends(get_current_user),
) -> StandardResponse[dict]:
    """Удалить транзакцию по id (только свою)"""
    tx = await transaction_service.get_transaction(
        db=db,
        transaction_id=transaction_id,
        user_id=current_user.id,
    )
    if not tx:
        raise NotFoundException(detail="Транзакция не найдена")

    await transaction_service.delete_transaction(db=db, db_obj=tx)
    return success_response(data={"message": "Транзакция удалена"})
