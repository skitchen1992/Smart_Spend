"""Тесты для app/modules/analytics/router.py"""

from typing import Any
from unittest.mock import AsyncMock, patch, ANY, MagicMock
import io

from fastapi import status

from app.modules.analytics.schemas import AnalyticsResponse, GroupAnalyticsResponse


class TestGetAnalytics:
    """Тесты для GET /analytics"""

    def test_get_analytics_success(self, client: Any, mock_user: Any) -> None:
        """Успешное получение аналитики"""
        analytics_data = AnalyticsResponse(
            period="2024-01",
            income=5000.0,
            expense=3000.0,
            by_category={"Food": 1000.0, "Transport": 2000.0},
            by_group={},
        )

        with patch("app.modules.analytics.router.analytics_service") as mock_service:
            mock_service.get_analytics = AsyncMock(return_value=analytics_data)

            response = client.get("/analytics")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert data["success"] is True
            assert data["code"] == status.HTTP_200_OK
            assert "data" in data
            assert data["data"]["period"] == "2024-01"
            assert data["data"]["income"] == 5000.0
            assert data["data"]["expense"] == 3000.0
            assert len(data["data"]["by_category"]) == 2

            mock_service.get_analytics.assert_called_once_with(
                db=ANY,
                user_id=int(mock_user.id),
                period=ANY,  # Может быть текущий месяц
            )

    def test_get_analytics_with_period(self, client: Any, mock_user: Any) -> None:
        """Получение аналитики с указанным периодом"""
        analytics_data = AnalyticsResponse(
            period="2024-02",
            income=6000.0,
            expense=4000.0,
            by_category={"Food": 2000.0, "Transport": 2000.0},
            by_group={},
        )

        with patch("app.modules.analytics.router.analytics_service") as mock_service:
            mock_service.get_analytics = AsyncMock(return_value=analytics_data)

            response = client.get("/analytics?period=2024-02")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert data["data"]["period"] == "2024-02"
            mock_service.get_analytics.assert_called_once_with(
                db=ANY,
                user_id=int(mock_user.id),
                period="2024-02",
            )


class TestGetGroupAnalytics:
    """Тесты для GET /analytics/groups/{group_id}"""

    def test_get_group_analytics_success(self, client: Any, mock_user: Any) -> None:
        """Успешное получение аналитики по группе"""
        group_id = 1
        group_analytics = GroupAnalyticsResponse(
            period="2024-01",
            group_id=group_id,
            group_name="Test Group",
            total_expense=5000.0,
            by_category={"Food": 3000.0, "Transport": 2000.0},
            member_expenses={"user_1": 3000.0, "user_2": 2000.0},
        )

        with patch("app.modules.analytics.router.analytics_service") as mock_service:
            mock_service.get_group_analytics = AsyncMock(return_value=group_analytics)

            response = client.get(f"/analytics/groups/{group_id}?period=2024-01")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert data["period"] == "2024-01"
            assert data["group_id"] == group_id
            assert data["group_name"] == "Test Group"
            assert data["total_expense"] == 5000.0
            assert len(data["by_category"]) == 2
            assert len(data["member_expenses"]) == 2

            mock_service.get_group_analytics.assert_called_once_with(
                db=ANY,
                user_id=mock_user.id,
                group_id=group_id,
                period="2024-01",
            )


class TestGetExpensesChart:
    """Тесты для GET /analytics/chart"""

    def test_get_expenses_chart_success(self, client: Any, mock_user: Any) -> None:
        """Успешное получение диаграммы расходов"""
        analytics_data = AnalyticsResponse(
            period="2024-01",
            income=5000.0,
            expense=3000.0,
            by_category={"Food": 1000.0, "Transport": 2000.0},
            by_group={},
        )

        # Создаем мок изображения PNG
        mock_image = b"fake_png_image_data"
        mock_buf = io.BytesIO(mock_image)

        # Мокаем matplotlib
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_autotext = MagicMock()
        mock_ax.pie.return_value = ([], [], [mock_autotext])  # wedges, texts, autotexts
        mock_fig.gca.return_value = mock_ax

        with patch("app.modules.analytics.router.analytics_service") as mock_service, patch(
            "app.modules.analytics.router.plt.subplots"
        ) as mock_subplots, patch(
            "app.modules.analytics.router.plt.savefig"
        ) as mock_savefig, patch(
            "app.modules.analytics.router.plt.close"
        ) as mock_close, patch(
            "app.modules.analytics.router.plt.get_cmap"
        ) as mock_get_cmap, patch(
            "app.modules.analytics.router.plt.rcParams", MagicMock()
        ), patch(
            "app.modules.analytics.router.io.BytesIO", return_value=mock_buf
        ):
            mock_service.get_analytics = AsyncMock(return_value=analytics_data)
            mock_subplots.return_value = (mock_fig, mock_ax)
            mock_get_cmap.return_value = lambda x: [0.5, 0.6]

            response = client.get("/analytics/chart?period=2024-01")

            assert response.status_code == status.HTTP_200_OK
            assert response.headers["content-type"] == "image/png"
            assert len(response.content) > 0

            mock_service.get_analytics.assert_called_once()
            mock_subplots.assert_called()
            mock_savefig.assert_called()
            mock_close.assert_called()

    def test_get_expenses_chart_empty_data(self, client: Any, mock_user: Any) -> None:
        """Получение диаграммы при отсутствии данных"""
        analytics_data = AnalyticsResponse(
            period="2024-01",
            income=0.0,
            expense=0.0,
            by_category={},
            by_group={},
        )

        # Создаем мок изображения PNG
        mock_image = b"fake_png_image_data"
        mock_buf = io.BytesIO(mock_image)

        # Мокаем matplotlib
        mock_fig = MagicMock()
        mock_ax = MagicMock()

        with patch("app.modules.analytics.router.analytics_service") as mock_service, patch(
            "app.modules.analytics.router.plt.subplots"
        ) as mock_subplots, patch(
            "app.modules.analytics.router.plt.savefig"
        ) as mock_savefig, patch(
            "app.modules.analytics.router.plt.close"
        ) as mock_close, patch(
            "app.modules.analytics.router.plt.rcParams", MagicMock()
        ), patch(
            "app.modules.analytics.router.io.BytesIO", return_value=mock_buf
        ):
            mock_service.get_analytics = AsyncMock(return_value=analytics_data)
            mock_subplots.return_value = (mock_fig, mock_ax)

            response = client.get("/analytics/chart?period=2024-01")

            assert response.status_code == status.HTTP_200_OK
            assert response.headers["content-type"] == "image/png"
            mock_service.get_analytics.assert_called_once()
            mock_subplots.assert_called()
            mock_savefig.assert_called()
            mock_close.assert_called()


class TestGetGroupChart:
    """Тесты для GET /analytics/chart/group/{group_id}"""

    def test_get_group_chart_success_category(self, client: Any, mock_user: Any) -> None:
        """Успешное получение диаграммы группы по категориям"""
        group_id = 1
        group_analytics = GroupAnalyticsResponse(
            period="2024-01",
            group_id=group_id,
            group_name="Test Group",
            total_expense=5000.0,
            by_category={"Food": 3000.0, "Transport": 2000.0},
            member_expenses={},
        )

        # Создаем мок изображения PNG
        mock_image = b"fake_png_image_data"
        mock_buf = io.BytesIO(mock_image)

        # Мокаем matplotlib
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_autotext = MagicMock()
        mock_ax.pie.return_value = ([], [], [mock_autotext])  # wedges, texts, autotexts
        mock_fig.gca.return_value = mock_ax
        mock_circle = MagicMock()

        with patch("app.modules.analytics.router.analytics_service") as mock_service, patch(
            "app.modules.analytics.router.plt.subplots"
        ) as mock_subplots, patch("app.modules.analytics.router.plt.savefig"), patch(
            "app.modules.analytics.router.plt.close"
        ), patch(
            "app.modules.analytics.router.plt.get_cmap"
        ) as mock_get_cmap, patch(
            "app.modules.analytics.router.plt.Circle", return_value=mock_circle
        ), patch(
            "app.modules.analytics.router.plt.rcParams", MagicMock()
        ), patch(
            "app.modules.analytics.router.io.BytesIO", return_value=mock_buf
        ):
            mock_service.get_group_analytics = AsyncMock(return_value=group_analytics)
            mock_subplots.return_value = (mock_fig, mock_ax)
            mock_get_cmap.return_value = lambda x: [0.5, 0.6]

            response = client.get(
                f"/analytics/chart/group/{group_id}?period=2024-01&chart_type=category"
            )

            assert response.status_code == status.HTTP_200_OK
            assert response.headers["content-type"] == "image/png"
            assert len(response.content) > 0

            mock_service.get_group_analytics.assert_called_once_with(
                db=ANY,
                user_id=int(mock_user.id),
                group_id=group_id,
                period="2024-01",
            )

    def test_get_group_chart_success_member(self, client: Any, mock_user: Any) -> None:
        """Успешное получение диаграммы группы по участникам"""
        group_id = 1
        group_analytics = GroupAnalyticsResponse(
            period="2024-01",
            group_id=group_id,
            group_name="Test Group",
            total_expense=5000.0,
            by_category={},
            member_expenses={"user_1": 3000.0, "user_2": 2000.0},
        )

        # Создаем мок изображения PNG
        mock_image = b"fake_png_image_data"
        mock_buf = io.BytesIO(mock_image)

        # Мокаем matplotlib
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_autotext = MagicMock()
        mock_ax.pie.return_value = ([], [], [mock_autotext])  # wedges, texts, autotexts
        mock_fig.gca.return_value = mock_ax
        mock_circle = MagicMock()

        with patch("app.modules.analytics.router.analytics_service") as mock_service, patch(
            "app.modules.analytics.router.plt.subplots"
        ) as mock_subplots, patch("app.modules.analytics.router.plt.savefig"), patch(
            "app.modules.analytics.router.plt.close"
        ), patch(
            "app.modules.analytics.router.plt.get_cmap"
        ) as mock_get_cmap, patch(
            "app.modules.analytics.router.plt.Circle", return_value=mock_circle
        ), patch(
            "app.modules.analytics.router.plt.rcParams", MagicMock()
        ), patch(
            "app.modules.analytics.router.io.BytesIO", return_value=mock_buf
        ):
            mock_service.get_group_analytics = AsyncMock(return_value=group_analytics)
            mock_subplots.return_value = (mock_fig, mock_ax)
            mock_get_cmap.return_value = lambda x: [0.5, 0.6]

            response = client.get(
                f"/analytics/chart/group/{group_id}?period=2024-01&chart_type=member"
            )

            assert response.status_code == status.HTTP_200_OK
            assert response.headers["content-type"] == "image/png"
            assert len(response.content) > 0

            mock_service.get_group_analytics.assert_called_once()

    def test_get_group_chart_empty_data(self, client: Any, mock_user: Any) -> None:
        """Получение диаграммы группы при отсутствии данных"""
        group_id = 1
        group_analytics = GroupAnalyticsResponse(
            period="2024-01",
            group_id=group_id,
            group_name="Test Group",
            total_expense=0.0,
            by_category={},
            member_expenses={},
        )

        # Создаем мок изображения PNG
        mock_image = b"fake_png_image_data"
        mock_buf = io.BytesIO(mock_image)

        # Мокаем matplotlib
        mock_fig = MagicMock()
        mock_ax = MagicMock()

        with patch("app.modules.analytics.router.analytics_service") as mock_service, patch(
            "app.modules.analytics.router.plt.subplots"
        ) as mock_subplots, patch(
            "app.modules.analytics.router.plt.savefig"
        ) as mock_savefig, patch(
            "app.modules.analytics.router.plt.close"
        ) as mock_close, patch(
            "app.modules.analytics.router.plt.rcParams", MagicMock()
        ), patch(
            "app.modules.analytics.router.io.BytesIO", return_value=mock_buf
        ):
            mock_service.get_group_analytics = AsyncMock(return_value=group_analytics)
            mock_subplots.return_value = (mock_fig, mock_ax)

            response = client.get(f"/analytics/chart/group/{group_id}?period=2024-01")

            assert response.status_code == status.HTTP_200_OK
            assert response.headers["content-type"] == "image/png"
            mock_service.get_group_analytics.assert_called_once()
            mock_subplots.assert_called()
            mock_savefig.assert_called()
            mock_close.assert_called()
