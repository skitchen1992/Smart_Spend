# Расчёт аналитики и статистики

from datetime import datetime
from calendar import monthrange
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.schemas import AnalyticsResponse
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
            raise ValueError(f"Неверный формат периода: {period}. Ожидается формат YYYY-MM") from e

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

        return AnalyticsResponse(
            period=period,
            income=income,
            expense=expense,
            by_category=by_category,
        )


analytics_service = AnalyticsService()
