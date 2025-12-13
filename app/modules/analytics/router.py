# Эндпоинты аналитики

import io
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

import matplotlib

matplotlib.use("Agg")  # Используем неинтерактивный бэкенд
import matplotlib.pyplot as plt  # noqa: E402

from app.core.db import get_db  # noqa: E402
from app.core.dto.response import StandardResponse, success_response  # noqa: E402
from app.core.dependencies import get_current_user  # noqa: E402
from app.modules.users.models import User  # noqa: E402
from app.modules.analytics.schemas import AnalyticsResponse, GroupAnalyticsResponse  # noqa: E402
from app.modules.analytics.service import analytics_service  # noqa: E402

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
    # Если период не указан или равен 'month', используем текущий месяц
    if period is None or period.lower() == "month":
        now = datetime.now()
        period = f"{now.year}-{now.month:02d}"

    result = await analytics_service.get_analytics(
        db=db,
        user_id=int(current_user.id),
        period=period,
    )

    return success_response(data=result)


@router.get("/groups/{group_id}", response_model=GroupAnalyticsResponse)
async def get_group_analytics(
    group_id: int,
    period: str = Query(..., description="Период в формате YYYY-MM"),
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
    # Если период не указан или равен 'month', используем текущий месяц
    if period is None or period.lower() == "month":
        now = datetime.now()
        period = f"{now.year}-{now.month:02d}"

    # Получаем аналитику
    analytics = await analytics_service.get_analytics(
        db=db,
        user_id=int(current_user.id),
        period=period,
    )

    # Если нет расходов по категориям, возвращаем пустое изображение
    if not analytics.by_category:
        # Создаем пустое изображение с сообщением
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.text(
            0.5, 0.5, "Нет данных о расходах\nпо категориям", ha="center", va="center", fontsize=16
        )
        ax.axis("off")

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=100)
        plt.close(fig)
        buf.seek(0)

        return Response(content=buf.read(), media_type="image/png")

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
        f"Расходы по категориям за период {period}", fontsize=16, fontweight="bold", pad=20
    )

    # Сохраняем в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=100)
    plt.close(fig)
    buf.seek(0)

    return Response(content=buf.read(), media_type="image/png")


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
    # Если период не указан или равен 'month', используем текущий месяц
    if period is None or period.lower() == "month":
        now = datetime.now()
        period = f"{now.year}-{now.month:02d}"

    # Получаем аналитику по группе
    analytics = await analytics_service.get_group_analytics(
        db=db,
        user_id=int(current_user.id),
        group_id=group_id,
        period=period,
    )

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

        title = f"Расходы по участникам группы\n'{analytics.group_name}' за {period}"
        color_map = "tab20c"
    else:
        # Диаграмма по категориям (по умолчанию)
        if not analytics.by_category:
            # Создаем пустое изображение с сообщением
            fig, ax = plt.subplots(figsize=(8, 8))
            ax.text(
                0.5,
                0.5,
                f"Нет данных о расходах\nв группе '{analytics.group_name}'\nза период {period}",
                ha="center",
                va="center",
                fontsize=16,
            )
            ax.axis("off")

            buf = io.BytesIO()
            plt.savefig(buf, format="png", bbox_inches="tight", dpi=100)
            plt.close(fig)
            buf.seek(0)

            return Response(content=buf.read(), media_type="image/png")

        labels = list(analytics.by_category.keys())
        amounts = list(analytics.by_category.values())
        title = f"Расходы по категориям в группе\n'{analytics.group_name}' за {period}"
        color_map = "Set3"

    if not labels:
        # Создаем пустое изображение с сообщением
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.text(
            0.5,
            0.5,
            f"Нет данных о расходах\nв группе '{analytics.group_name}'\nза период {period}",
            ha="center",
            va="center",
            fontsize=16,
        )
        ax.axis("off")

        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", dpi=100)
        plt.close(fig)
        buf.seek(0)

        return Response(content=buf.read(), media_type="image/png")

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

    return Response(content=buf.read(), media_type="image/png")
