# app/modules/transactions/router.py


from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
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
    PaginatedTransactionResponse,
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
        user_id=int(current_user.id),
        transaction_in=transaction_in,
    )
    data = TransactionResponse.model_validate(tx)
    return success_response(data=data, code=201)


@router.get(
    "",
    response_model=StandardResponse[PaginatedTransactionResponse],
)
async def list_transactions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    category: str | None = Query(None, description="Фильтр по категории"),
    date_from: str | None = Query(None, description="Начальная дата (YYYY-MM-DD)"),
    date_to: str | None = Query(None, description="Конечная дата (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Размер страницы"),
) -> StandardResponse[PaginatedTransactionResponse]:
    """Получить список транзакций текущего пользователя с фильтрами и пагинацией"""
    result = await transaction_service.list_transactions(
        db=db,
        user_id=int(current_user.id),
        category=category,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size,
    )

    return success_response(data=result)


@router.get(
    "/export",
    response_class=Response,
)
async def export_transactions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    category: str | None = Query(None, description="Фильтр по категории"),
    date_from: str | None = Query(None, description="Начальная дата (YYYY-MM-DD)"),
    date_to: str | None = Query(None, description="Конечная дата (YYYY-MM-DD)"),
) -> Response:
    """Экспортировать транзакции текущего пользователя в CSV файл"""
    csv_content = await transaction_service.export_transactions_to_csv(
        db=db,
        user_id=int(current_user.id),
        category=category,
        date_from=date_from,
        date_to=date_to,
    )

    return Response(
        content=csv_content.encode("utf-8"),
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="transactions.csv"',
        },
    )


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
        user_id=int(current_user.id),
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
        user_id=int(current_user.id),
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
        user_id=int(current_user.id),
    )
    if not tx:
        raise NotFoundException(detail="Транзакция не найдена")

    await transaction_service.delete_transaction(db=db, db_obj=tx)
    return success_response(data={"message": "Транзакция удалена"})
