# Расчёт аналитики и статистики

from datetime import datetime
from calendar import monthrange

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.schemas import AnalyticsResponse, GroupAnalyticsResponse
from app.modules.groups.repository import group_repository
from app.modules.transactions.repository import transaction_repository


class AnalyticsService:
    """Сервис для расчета аналитики по транзакциям"""

    def _parse_period(self, period: str) -> tuple[datetime, datetime]:
        """
        Парсит период в формате YYYY-MM и возвращает начало и конец месяца
        """
        try:
            year, month = map(int, period.split("-"))
            # Начало месяца
            date_from = datetime(year, month, 1, 0, 0, 0)
            # Конец месяца
            last_day = monthrange(year, month)[1]
            date_to = datetime(year, month, last_day, 23, 59, 59)
            return date_from, date_to
        except (ValueError, IndexError) as e:
            raise HTTPException(404,f"Неверный формат периода: {period}. Ожидается формат YYYY-MM") from e

    async def get_analytics(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        period: str,
    ) -> AnalyticsResponse:
        """
        Получить аналитику по транзакциям за указанный период
        period: строка в формате YYYY-MM (например, "2025-01")
        """
        # Парсим период
        date_from, date_to = self._parse_period(period)

        # Получаем доходы
        income = await transaction_repository.get_income_sum(
            db=db,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
        )

        # Получаем расходы
        expense = await transaction_repository.get_expense_sum(
            db=db,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
        )

        # Получаем расходы по категориям
        by_category = await transaction_repository.get_expenses_by_category(
            db=db,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
        )

        # Получаем расходы по группам
        by_group = await transaction_repository.get_expenses_by_group(
            db=db,
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
        )

        return AnalyticsResponse(
            period=period,
            income=income,
            expense=expense,
            by_category=by_category,
            by_group=by_group,
        )

    async def get_group_analytics(
            self,
            db: AsyncSession,
            *,
            user_id: int,
            group_id: int,
            period: str,
    ) -> GroupAnalyticsResponse:
        """
        Получить аналитику по расходам в конкретной группе за указанный период

        Args:
            db: Сессия БД
            user_id: ID пользователя, запрашивающего аналитику
            group_id: ID группы
            period: Период в формате YYYY-MM

        Returns:
            GroupAnalyticsResponse: Аналитика по группе
        """
        # Проверяем, состоит ли пользователь в группе
        group = await group_repository.get_group(
            db=db,
            group_id=group_id,
            id_user=user_id
        )

        if not group:
            raise HTTPException(
                status_code=403,
                detail="User is not a member of this group or group does not exist"
            )

        # Парсим период
        date_from, date_to = self._parse_period(period)

        # Получаем общие расходы группы
        total_expense = await transaction_repository.get_group_expense_sum(
            db=db,
            group_id=group_id,
            date_from=date_from,
            date_to=date_to,
        )

        # Получаем расходы по категориям для группы
        by_category = await transaction_repository.get_group_expenses_by_category(
            db=db,
            group_id=group_id,
            date_from=date_from,
            date_to=date_to,
        )

        # Получаем расходы по участникам группы
        member_expenses = await transaction_repository.get_group_expenses_by_member(
            db=db,
            group_id=group_id,
            date_from=date_from,
            date_to=date_to,
        )

        return GroupAnalyticsResponse(
            period=period,
            group_id=group_id,
            group_name=group.name,
            total_expense=total_expense,
            by_category=by_category,
            member_expenses=member_expenses,
        )

analytics_service = AnalyticsService()
