"""Тесты для app/modules/transactions/router.py"""

from unittest.mock import ANY, AsyncMock, patch

import pytest
from fastapi import status
from sqlalchemy.exc import SQLAlchemyError


class TestExportTransactions:
    """Тесты для GET /transactions/export"""

    def test_export_transactions_success_no_filters(self, client, mock_user):
        """Успешный экспорт транзакций без фильтров"""
        csv_content = (
            "\ufeffID,Название,Сумма,Тип,Категория,Описание,Дата создания,Дата обновления\n"
            "1,Test Transaction,100.0,expense,Food,Test description,2024-01-01 12:00:00,2024-01-01 12:00:00\n"
        )

        with patch(
            "app.modules.transactions.router.transaction_service.export_transactions_to_csv"
        ) as mock_export:
            mock_export.return_value = csv_content

            response = client.get("/transactions/export")

            assert response.status_code == status.HTTP_200_OK
            assert response.headers["content-type"] == "text/csv; charset=utf-8"
            assert (
                response.headers["content-disposition"] == 'attachment; filename="transactions.csv"'
            )
            assert response.content.decode("utf-8") == csv_content
            mock_export.assert_called_once_with(
                db=ANY,
                user_id=1,
                category=None,
                date_from=None,
                date_to=None,
            )

    def test_export_transactions_with_category_filter(self, client, mock_user):
        """Успешный экспорт транзакций с фильтром по категории"""
        csv_content = (
            "\ufeffID,Название,Сумма,Тип,Категория,Описание,Дата создания,Дата обновления\n"
        )

        with patch(
            "app.modules.transactions.router.transaction_service.export_transactions_to_csv"
        ) as mock_export:
            mock_export.return_value = csv_content

            response = client.get("/transactions/export?category=Food")

            assert response.status_code == status.HTTP_200_OK
            mock_export.assert_called_once_with(
                db=ANY,
                user_id=1,
                category="Food",
                date_from=None,
                date_to=None,
            )

    def test_export_transactions_with_date_from_filter(self, client, mock_user):
        """Успешный экспорт транзакций с фильтром по начальной дате"""
        csv_content = (
            "\ufeffID,Название,Сумма,Тип,Категория,Описание,Дата создания,Дата обновления\n"
            "1,Test Transaction,100.0,expense,Food,Test description,2024-01-01 12:00:00,2024-01-01 12:00:00\n"
        )

        with patch(
            "app.modules.transactions.router.transaction_service.export_transactions_to_csv"
        ) as mock_export:
            mock_export.return_value = csv_content

            response = client.get("/transactions/export?date_from=2024-01-01")

            assert response.status_code == status.HTTP_200_OK
            mock_export.assert_called_once_with(
                db=ANY,
                user_id=1,
                category=None,
                date_from="2024-01-01",
                date_to=None,
            )

    def test_export_transactions_with_date_to_filter(self, client, mock_user):
        """Успешный экспорт транзакций с фильтром по конечной дате"""
        csv_content = (
            "\ufeffID,Название,Сумма,Тип,Категория,Описание,Дата создания,Дата обновления\n"
            "1,Test Transaction,100.0,expense,Food,Test description,2024-01-01 12:00:00,2024-01-01 12:00:00\n"
        )

        with patch(
            "app.modules.transactions.router.transaction_service.export_transactions_to_csv"
        ) as mock_export:
            mock_export.return_value = csv_content

            response = client.get("/transactions/export?date_to=2024-12-31")

            assert response.status_code == status.HTTP_200_OK
            mock_export.assert_called_once_with(
                db=ANY,
                user_id=1,
                category=None,
                date_from=None,
                date_to="2024-12-31",
            )

    def test_export_transactions_with_all_filters(self, client, mock_user):
        """Успешный экспорт транзакций со всеми фильтрами"""
        csv_content = (
            "\ufeffID,Название,Сумма,Тип,Категория,Описание,Дата создания,Дата обновления\n"
            "1,Test Transaction,100.0,expense,Food,Test description,2024-01-01 12:00:00,2024-01-01 12:00:00\n"
        )

        with patch(
            "app.modules.transactions.router.transaction_service.export_transactions_to_csv"
        ) as mock_export:
            mock_export.return_value = csv_content

            response = client.get(
                "/transactions/export?category=Food&date_from=2024-01-01&date_to=2024-12-31"
            )

            assert response.status_code == status.HTTP_200_OK
            mock_export.assert_called_once_with(
                db=ANY,
                user_id=1,
                category="Food",
                date_from="2024-01-01",
                date_to="2024-12-31",
            )

    def test_export_transactions_empty_result(self, client, mock_user):
        """Экспорт транзакций с пустым результатом (только заголовки)"""
        csv_content = (
            "\ufeffID,Название,Сумма,Тип,Категория,Описание,Дата создания,Дата обновления\n"
        )

        with patch(
            "app.modules.transactions.router.transaction_service.export_transactions_to_csv"
        ) as mock_export:
            mock_export.return_value = csv_content

            response = client.get("/transactions/export")

            assert response.status_code == status.HTTP_200_OK
            assert response.content.decode("utf-8") == csv_content
            mock_export.assert_called_once()

    def test_export_transactions_service_raises_exception(self, client, mock_user):
        """Проверка обработки исключения от сервиса"""
        with patch(
            "app.modules.transactions.router.transaction_service.export_transactions_to_csv"
        ) as mock_export:
            mock_export.side_effect = SQLAlchemyError("Database error")

            response = client.get("/transactions/export")

            # FastAPI должен вернуть 500 ошибку при необработанном исключении
            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            mock_export.assert_called_once()
