"""CRUD-тесты для app/modules/transactions/router.py"""

from unittest.mock import ANY, AsyncMock, patch

from fastapi import status


def _tx_dict(
    *,
    tx_id: int = 1,
    user_id: int = 1,
    title: str = "Test Transaction",
    amount: float = 100.0,
    tx_type: str = "expense",
    category: str = "Food",
    description: str = "Test description",
    transaction_to_group: int = 0,
    created_at: str = "2024-01-01T12:00:00",
    updated_at: str = "2024-01-01T12:00:00",
):
    return {
        "id": tx_id,
        "user_id": user_id,
        "title": title,
        "amount": amount,
        "type": tx_type,
        "category": category,
        "description": description,
        "transaction_to_group": transaction_to_group,
        "created_at": created_at,
        "updated_at": updated_at,
    }


class TestTransactionsCRUD:
    """Тесты для CRUD эндпоинтов /transactions"""

    def test_create_transaction_success(self, client, mock_user):
        payload = {
            "title": "Coffee",
            "amount": 10.5,
            "type": "expense",
            "category": "Food",
            "description": "Latte",
            "transaction_to_group": 0,
        }

        service_result = _tx_dict(
            tx_id=10,
            user_id=1,
            title="Coffee",
            amount=10.5,
            tx_type="expense",
            category="Food",
            description="Latte",
            transaction_to_group=0,
        )

        with patch(
            "app.modules.transactions.router.transaction_service.create_transaction",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = service_result

            response = client.post("/transactions", json=payload)

            assert response.status_code == status.HTTP_201_CREATED
            body = response.json()
            assert body["success"] is True
            assert body["code"] == 201
            assert body["data"]["id"] == 10
            assert body["data"]["user_id"] == 1
            assert body["data"]["title"] == "Coffee"
            assert body["data"]["amount"] == 10.5
            assert body["data"]["transaction_to_group"] == 0

            mock_create.assert_called_once_with(
                db=ANY,
                user_id=1,
                transaction_in=ANY,
            )

    def test_list_transactions_success(self, client, mock_user):
        service_result = {
            "items": [
                _tx_dict(tx_id=1, user_id=1, title="Coffee", amount=10.0, transaction_to_group=0),
                _tx_dict(tx_id=2, user_id=1, title="Taxi", amount=20.0, transaction_to_group=0),
            ],
            "total": 2,
            "page": 1,
            "page_size": 20,
            "pages": 1,
        }

        with patch(
            "app.modules.transactions.router.transaction_service.list_transactions",
            new_callable=AsyncMock,
        ) as mock_list:
            mock_list.return_value = service_result

            response = client.get("/transactions")

            assert response.status_code == status.HTTP_200_OK
            body = response.json()
            assert body["success"] is True
            assert body["data"]["total"] == 2
            assert len(body["data"]["items"]) == 2
            assert body["data"]["items"][0]["id"] == 1
            assert body["data"]["items"][1]["id"] == 2

            mock_list.assert_called_once_with(
                db=ANY,
                user_id=1,
                category=None,
                date_from=None,
                date_to=None,
                page=1,
                page_size=20,
            )

    def test_list_transactions_with_filters(self, client, mock_user):
        service_result = {"items": [], "total": 0, "page": 1, "page_size": 20, "pages": 0}

        with patch(
            "app.modules.transactions.router.transaction_service.list_transactions",
            new_callable=AsyncMock,
        ) as mock_list:
            mock_list.return_value = service_result

            response = client.get(
                "/transactions?category=Food&date_from=2024-01-01&date_to=2024-12-31&page=1&page_size=20"
            )

            assert response.status_code == status.HTTP_200_OK

            mock_list.assert_called_once_with(
                db=ANY,
                user_id=1,
                category="Food",
                date_from="2024-01-01",
                date_to="2024-12-31",
                page=1,
                page_size=20,
            )

    def test_get_transaction_success(self, client, mock_user):
        service_result = _tx_dict(
            tx_id=7,
            user_id=1,
            title="Dinner",
            amount=50.0,
            transaction_to_group=0,
        )

        with patch(
            "app.modules.transactions.router.transaction_service.get_transaction",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = service_result

            response = client.get("/transactions/7")

            assert response.status_code == status.HTTP_200_OK
            body = response.json()
            assert body["success"] is True
            assert body["data"]["id"] == 7
            assert body["data"]["title"] == "Dinner"
            assert body["data"]["transaction_to_group"] == 0

            mock_get.assert_called_once_with(
                db=ANY,
                transaction_id=7,
                user_id=1,
            )

    def test_get_transaction_not_found(self, client, mock_user):
        with patch(
            "app.modules.transactions.router.transaction_service.get_transaction",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = None

            response = client.get("/transactions/999")

            assert response.status_code == status.HTTP_404_NOT_FOUND
            mock_get.assert_called_once_with(
                db=ANY,
                transaction_id=999,
                user_id=1,
            )

    def test_update_transaction_success(self, client, mock_user):
        payload = {
            "title": "Updated",
            "amount": 123.45,
            "category": "Food",
            "description": "Updated description",
            "type": "expense",
        }

        existing_tx = _tx_dict(tx_id=5, user_id=1, transaction_to_group=0)
        updated_tx = _tx_dict(
            tx_id=5,
            user_id=1,
            title="Updated",
            amount=123.45,
            category="Food",
            description="Updated description",
            tx_type="expense",
            transaction_to_group=0,
        )

        with patch(
            "app.modules.transactions.router.transaction_service.get_transaction",
            new_callable=AsyncMock,
        ) as mock_get, patch(
            "app.modules.transactions.router.transaction_service.update_transaction",
            new_callable=AsyncMock,
        ) as mock_update:
            mock_get.return_value = existing_tx
            mock_update.return_value = updated_tx

            response = client.put("/transactions/5", json=payload)

            assert response.status_code == status.HTTP_200_OK
            body = response.json()
            assert body["success"] is True
            assert body["data"]["id"] == 5
            assert body["data"]["title"] == "Updated"
            assert body["data"]["amount"] == 123.45
            assert body["data"]["transaction_to_group"] == 0

            mock_get.assert_called_once_with(
                db=ANY,
                transaction_id=5,
                user_id=1,
            )
            mock_update.assert_called_once_with(
                db=ANY,
                db_obj=ANY,
                transaction_in=ANY,
            )

    def test_update_transaction_not_found(self, client, mock_user):
        payload = {"title": "Updated"}

        with patch(
            "app.modules.transactions.router.transaction_service.get_transaction",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = None

            response = client.put("/transactions/404", json=payload)

            assert response.status_code == status.HTTP_404_NOT_FOUND
            mock_get.assert_called_once_with(
                db=ANY,
                transaction_id=404,
                user_id=1,
            )

    def test_delete_transaction_success(self, client, mock_user):
        existing_tx = _tx_dict(tx_id=6, user_id=1, transaction_to_group=0)

        with patch(
            "app.modules.transactions.router.transaction_service.get_transaction",
            new_callable=AsyncMock,
        ) as mock_get, patch(
            "app.modules.transactions.router.transaction_service.delete_transaction",
            new_callable=AsyncMock,
        ) as mock_delete:
            mock_get.return_value = existing_tx
            mock_delete.return_value = None

            response = client.delete("/transactions/6")

            assert response.status_code == status.HTTP_200_OK
            body = response.json()
            assert body["success"] is True
            assert body["data"]["message"] == "Транзакция удалена"

            mock_get.assert_called_once_with(
                db=ANY,
                transaction_id=6,
                user_id=1,
            )
            mock_delete.assert_called_once_with(
                db=ANY,
                db_obj=ANY,
            )

    def test_delete_transaction_not_found(self, client, mock_user):
        with patch(
            "app.modules.transactions.router.transaction_service.get_transaction",
            new_callable=AsyncMock,
        ) as mock_get:
            mock_get.return_value = None

            response = client.delete("/transactions/404")

            assert response.status_code == status.HTTP_404_NOT_FOUND
            mock_get.assert_called_once_with(
                db=ANY,
                transaction_id=404,
                user_id=1,
            )
