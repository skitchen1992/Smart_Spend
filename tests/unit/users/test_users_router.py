"""Тесты для app/modules/users/router.py"""

from typing import Any
from unittest.mock import AsyncMock, patch, ANY, MagicMock
from datetime import datetime, timezone

from fastapi import status


class TestGetMe:
    """Тесты для GET /users/me"""

    def test_get_me_success(self, client: Any, mock_user: Any) -> None:
        """Успешное получение информации о текущем пользователе"""
        response = client.get("/users/me")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["success"] is True
        assert data["code"] == status.HTTP_200_OK
        assert "data" in data
        assert data["data"]["id"] == mock_user.id
        assert data["data"]["username"] == mock_user.username
        assert data["data"]["email"] == mock_user.email
        assert data["data"]["full_name"] == mock_user.full_name
        assert data["data"]["is_active"] == mock_user.is_active


class TestGetUser:
    """Тесты для GET /users/{user_id}"""

    def test_get_user_success(self, client: Any, mock_user: Any) -> None:
        """Успешное получение информации о пользователе по ID"""
        user_id = 2
        another_user = MagicMock()
        another_user.id = user_id
        another_user.username = "another_user"
        another_user.email = "another@example.com"
        another_user.full_name = "Another User"
        another_user.is_active = True
        another_user.created_at = datetime.now(timezone.utc)
        another_user.updated_at = None

        with patch("app.modules.users.router.user_service") as mock_user_service:
            mock_user_service.get_user_by_id = AsyncMock(return_value=another_user)

            response = client.get(f"/users/{user_id}")

            assert response.status_code == status.HTTP_200_OK
            data = response.json()

            assert data["success"] is True
            assert data["code"] == status.HTTP_200_OK
            assert "data" in data
            assert data["data"]["id"] == user_id
            assert data["data"]["username"] == "another_user"
            assert data["data"]["email"] == "another@example.com"

            mock_user_service.get_user_by_id.assert_called_once_with(
                db=ANY,
                user_id=user_id,
            )

    def test_get_user_not_found(self, client: Any) -> None:
        """Получение несуществующего пользователя"""
        user_id = 999

        with patch("app.modules.users.router.user_service") as mock_user_service:
            mock_user_service.get_user_by_id = AsyncMock(return_value=None)

            response = client.get(f"/users/{user_id}")

            assert response.status_code == status.HTTP_404_NOT_FOUND
            mock_user_service.get_user_by_id.assert_called_once_with(
                db=ANY,
                user_id=user_id,
            )
