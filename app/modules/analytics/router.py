# Эндпоинты аналитики

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.dto.response import StandardResponse, success_response
from app.core.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.analytics.schemas import AnalyticsResponse, GroupAnalyticsResponse
from app.modules.analytics.service import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get(
    "",
    response_model=StandardResponse[AnalyticsResponse],
)
async def get_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    period: str
    | None = Query(
        None,
        description="Период в формате YYYY-MM (например, 2025-01) или 'month' для текущего месяца. Если не указан, используется текущий месяц",
    ),
) -> StandardResponse[AnalyticsResponse]:
    """
    Получить аналитику по расходам за указанный период.

    Возвращает:
    - period: период в формате YYYY-MM
    - income: общий доход за период
    - expense: общий расход за период
    - by_category: расходы по категориям
    """
    result = await analytics_service.get_analytics(
        db=db,
        user_id=int(current_user.id),
        period=period,
    )

    return success_response(data=result)


@router.get("/groups/{group_id}", response_model=GroupAnalyticsResponse)
async def get_group_analytics(
    group_id: int,
    period: str
    | None = Query(
        None,
        description="Период в формате YYYY-MM (например, 2025-01) или 'month' для текущего месяца. Если не указан, используется текущий месяц",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> GroupAnalyticsResponse:
    """
    Получить аналитику по расходам в конкретной группе за указанный период
    """
    return await analytics_service.get_group_analytics(
        db=db,
        user_id=int(current_user.id),
        group_id=group_id,
        period=period,
    )


@router.get(
    "/chart",
    response_class=Response,
)
async def get_expenses_chart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    period: str
    | None = Query(
        None,
        description="Период в формате YYYY-MM (например, 2025-01) или 'month' для текущего месяца. Если не указан, используется текущий месяц",
    ),
) -> Response:
    """
    Получить круговую диаграмму расходов по категориям за указанный период.

    Возвращает изображение в формате PNG.
    """
    chart_bytes = await analytics_service.get_expenses_chart(
        db=db,
        user_id=int(current_user.id),
        period=period,
    )

    return Response(content=chart_bytes, media_type="image/png")


@router.get(
    "/chart/group/{group_id}",
    response_class=Response,
)
async def get_group_chart(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    period: str
    | None = Query(
        None,
        description="Период в формате YYYY-MM (например, 2025-01) или 'month' для текущего месяца. Если не указан, используется текущий месяц",
    ),
    chart_type: str = Query(
        "category",
        description="Тип диаграммы: 'category' - по категориям, 'member' - по участникам",
    ),
) -> Response:
    """
    Получить диаграмму расходов конкретной группы за указанный период.

    Возвращает изображение в формате PNG.

    Параметры:
    - group_id: ID группы
    - period: период в формате YYYY-MM
    - chart_type: тип диаграммы ('category' или 'member')
    """
    chart_bytes = await analytics_service.get_group_chart(
        db=db,
        user_id=int(current_user.id),
        group_id=group_id,
        period=period,
        chart_type=chart_type,
    )

    return Response(content=chart_bytes, media_type="image/png")
