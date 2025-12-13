# Расчёт аналитики и статистики

import io
from calendar import monthrange
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.analytics.schemas import AnalyticsResponse, GroupAnalyticsResponse
from app.modules.groups.repository import group_repository
from app.modules.transactions.repository import transaction_repository

import matplotlib

matplotlib.use("Agg")  # Используем неинтерактивный бэкенд
import matplotlib.pyplot as plt  # noqa: E402


class AnalyticsService:
    """Сервис для расчета аналитики по транзакциям"""

    def _normalize_period(self, period: str | None) -> str:
        """
        Нормализует период в формат YYYY-MM.
        Если период не указан или равен 'month', возвращает текущий месяц.
        """
        if period is None or period.lower() == "month":
            now = datetime.now()
            return f"{now.year}-{now.month:02d}"
        return period

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
            raise HTTPException(
                404, f"Неверный формат периода: {period}. Ожидается формат YYYY-MM"
            ) from e

    async def get_analytics(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        period: str | None = None,
    ) -> AnalyticsResponse:
        """
        Получить аналитику по транзакциям за указанный период
        period: строка в формате YYYY-MM (например, "2025-01") или None/'month' для текущего месяца
        """
        # Нормализуем период
        normalized_period = self._normalize_period(period)
        # Парсим период
        date_from, date_to = self._parse_period(normalized_period)

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
            period=normalized_period,
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
        period: str | None = None,
    ) -> GroupAnalyticsResponse:
        """
        Получить аналитику по расходам в конкретной группе за указанный период

        Args:
            db: Сессия БД
            user_id: ID пользователя, запрашивающего аналитику
            group_id: ID группы
            period: Период в формате YYYY-MM или None/'month' для текущего месяца

        Returns:
            GroupAnalyticsResponse: Аналитика по группе
        """
        # Проверяем, состоит ли пользователь в группе
        group = await group_repository.get_group(db=db, group_id=group_id, id_user=user_id)

        if not group:
            raise HTTPException(
                status_code=403,
                detail="Пользователь не является участником этой группы или группа не существует",
            )

        # Нормализуем период
        normalized_period = self._normalize_period(period)
        # Парсим период
        date_from, date_to = self._parse_period(normalized_period)

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
            period=normalized_period,
            group_id=group_id,
            group_name=str(group.name),
            total_expense=total_expense,
            by_category=by_category,
            member_expenses=member_expenses,
        )

    def _create_empty_chart(self, message: str) -> bytes:
        """Создает пустое изображение с сообщением"""
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=16)
        ax.axis("off")

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=100)
        plt.close(fig)
        buf.seek(0)
        return buf.read()

    async def get_expenses_chart(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        period: str | None = None,
    ) -> bytes:
        """
        Создает круговую диаграмму расходов по категориям за указанный период.

        Args:
            db: Сессия БД
            user_id: ID пользователя
            period: Период в формате YYYY-MM или None/'month' для текущего месяца

        Returns:
            bytes: Изображение в формате PNG
        """
        # Получаем аналитику (метод сам нормализует период)
        analytics = await self.get_analytics(
            db=db,
            user_id=user_id,
            period=period,
        )

        # Получаем нормализованный период из результата
        normalized_period = analytics.period

        # Если нет расходов по категориям, возвращаем пустое изображение
        if not analytics.by_category:
            return self._create_empty_chart("Нет данных о расходах\nпо категориям")

        # Подготовка данных для диаграммы
        categories = list(analytics.by_category.keys())
        amounts = list(analytics.by_category.values())

        # Создаем круговую диаграмму
        fig, ax = plt.subplots(figsize=(10, 8))

        # Используем русские шрифты для корректного отображения
        plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "sans-serif"]
        plt.rcParams["axes.unicode_minus"] = False

        # Создаем круговую диаграмму
        cmap = plt.get_cmap("Set3")
        colors = [cmap(i / len(categories)) for i in range(len(categories))]
        wedges, texts, autotexts = ax.pie(  # type: ignore[misc]
            amounts,
            labels=categories,
            autopct="%1.1f%%",
            startangle=90,
            colors=colors,  # type: ignore[arg-type]
            textprops={"fontsize": 10},
        )

        # Улучшаем отображение процентов
        for autotext in autotexts:
            autotext.set_color("black")
            autotext.set_fontweight("bold")

        # Добавляем заголовок
        ax.set_title(
            f"Расходы по категориям за период {normalized_period}",
            fontsize=16,
            fontweight="bold",
            pad=20,
        )

        # Сохраняем в буфер
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=100)
        plt.close(fig)
        buf.seek(0)

        return buf.read()

    async def get_group_chart(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        group_id: int,
        period: str | None = None,
        chart_type: str = "category",
    ) -> bytes:
        """
        Создает диаграмму расходов конкретной группы за указанный период.

        Args:
            db: Сессия БД
            user_id: ID пользователя
            group_id: ID группы
            period: Период в формате YYYY-MM или None/'month' для текущего месяца
            chart_type: Тип диаграммы ('category' или 'member')

        Returns:
            bytes: Изображение в формате PNG
        """
        # Получаем аналитику по группе (метод сам нормализует период)
        analytics = await self.get_group_analytics(
            db=db,
            user_id=user_id,
            group_id=group_id,
            period=period,
        )

        # Получаем нормализованный период из результата
        normalized_period = analytics.period

        # Определяем данные для диаграммы в зависимости от типа
        if chart_type == "member" and analytics.member_expenses:
            # Диаграмма по участникам
            labels = []
            amounts = []

            for member_key, amount in analytics.member_expenses.items():
                if amount > 0:
                    try:
                        # Пробуем разные форматы ключей
                        if member_key.startswith("user_"):
                            user_id = int(member_key.replace("user_", ""))
                            labels.append(f"Участник {user_id}")
                        elif member_key.startswith("id: "):
                            # Формат "id: 1"
                            user_id = int(member_key.split(": ")[1])
                            labels.append(f"Участник {user_id}")
                        else:
                            labels.append(member_key)
                        amounts.append(amount)
                    except (ValueError, IndexError):
                        # Если не удалось распарсить, используем ключ как есть
                        labels.append(member_key)
                        amounts.append(amount)

            title = f"Расходы по участникам группы\n'{analytics.group_name}' за {normalized_period}"
            color_map = "tab20c"
        else:
            # Диаграмма по категориям (по умолчанию)
            if not analytics.by_category:
                return self._create_empty_chart(
                    f"Нет данных о расходах\nв группе '{analytics.group_name}'\nза период {normalized_period}"
                )

            labels = list(analytics.by_category.keys())
            amounts = list(analytics.by_category.values())
            title = (
                f"Расходы по категориям в группе\n'{analytics.group_name}' за {normalized_period}"
            )
            color_map = "Set3"

        if not labels:
            return self._create_empty_chart(
                f"Нет данных о расходах\nв группе '{analytics.group_name}'\nза период {normalized_period}"
            )

        # Создаем круговую диаграмму
        fig, ax = plt.subplots(figsize=(12, 10))

        plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "sans-serif"]
        plt.rcParams["axes.unicode_minus"] = False

        # Ограничиваем количество отображаемых элементов (если их слишком много)
        max_items = 10
        if len(labels) > max_items:
            # Сортируем по убыванию суммы
            sorted_data = sorted(zip(labels, amounts), key=lambda x: x[1], reverse=True)
            top_labels, top_amounts = zip(*sorted_data[: max_items - 1])

            # Объединяем остальное в "Другие"
            other_labels, other_amounts = zip(*sorted_data[max_items - 1 :])
            other_total = sum(other_amounts)

            labels = list(top_labels) + ["Другие"]
            amounts = list(top_amounts) + [other_total]

        # Создаем круговую диаграмму
        cmap = plt.get_cmap(color_map)
        colors = [cmap(i / len(labels)) for i in range(len(labels))]
        wedges, texts, autotexts = ax.pie(
            amounts,
            labels=labels,
            autopct=lambda pct: f"{pct:.1f}%\n({pct * sum(amounts) / 100:.0f} руб.)",
            startangle=90,
            colors=colors,
            textprops={"fontsize": 9},
            pctdistance=0.85,
        )

        # Улучшаем отображение
        for autotext in autotexts:
            autotext.set_color("black")
            autotext.set_fontweight("bold")

        # Добавляем заголовок
        ax.set_title(title, fontsize=16, fontweight="bold", pad=20)

        # Добавляем общую сумму расходов в центре
        centre_circle = plt.Circle((0, 0), 0.70, fc="white")
        fig.gca().add_artist(centre_circle)

        ax.text(
            0,
            0,
            f"Всего:\n{sum(amounts):.0f} руб.",
            ha="center",
            va="center",
            fontsize=14,
            fontweight="bold",
        )

        # Сохраняем в буфер
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=120)
        plt.close(fig)
        buf.seek(0)

        return buf.read()


analytics_service = AnalyticsService()
