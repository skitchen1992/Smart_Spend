"""Тесты для app/modules/auth/router.py"""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import status

from app.modules.auth.schemas import Login, RefreshTokenRequest
from app.modules.users.schemas import UserCreate
from app.core.exceptions import CredentialsException


class TestRegister:
    """Тесты для POST /auth/register"""

    def test_register_success(self, client, mock_user):
        """Успешная регистрация пользователя"""
        user_data = UserCreate(
            username="newuser",
            email="newuser@example.com",
            full_name="New User",
            password="password123",
        )
        tokens = {"access_token": "test_access_token", "refresh_token": "test_refresh_token"}

        with (
            patch("app.modules.auth.router.user_service") as mock_user_service,
            patch("app.modules.auth.router.auth_service") as mock_auth_service,
        ):
            mock_user_service.create_user = AsyncMock(return_value=mock_user)
            mock_auth_service.generate_tokens = AsyncMock(return_value=tokens)

            response = client.post("/auth/register", json=user_data.model_dump())

            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["success"] is True
            assert data.get("code") in [status.HTTP_200_OK, status.HTTP_201_CREATED]
            assert "data" in data
            assert "access_token" in data["data"]
            assert "refresh_token" in data["data"]
            mock_user_service.create_user.assert_called_once()
            mock_auth_service.generate_tokens.assert_called_once()


class TestLogin:
    """Тесты для POST /auth/login"""

    def test_login_success(self, client, mock_user):
        """Успешный вход"""
        login_data = Login(username="testuser", password="test_password_123")
        tokens = {"access_token": "test_access_token", "refresh_token": "test_refresh_token"}

        with patch("app.modules.auth.router.auth_service") as mock_auth_service:
            mock_auth_service.authenticate_user = AsyncMock(return_value=mock_user)
            mock_auth_service.generate_tokens = AsyncMock(return_value=tokens)

            response = client.post("/auth/login", json=login_data.model_dump())

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["code"] == status.HTTP_200_OK
            assert "data" in data
            assert "access_token" in data["data"]
            assert "refresh_token" in data["data"]
            mock_auth_service.authenticate_user.assert_called_once()
            mock_auth_service.generate_tokens.assert_called_once()

    def test_login_invalid_credentials(self, client):
        """Вход с неверными учетными данными"""
        login_data = Login(username="testuser", password="wrong_password")

        with patch("app.modules.auth.router.auth_service") as mock_auth_service:
            mock_auth_service.authenticate_user = AsyncMock(return_value=None)

            response = client.post("/auth/login", json=login_data.model_dump())

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            data = response.json()
            assert "success" in data or "detail" in data
            if "success" in data:
                assert data["success"] is False
            mock_auth_service.authenticate_user.assert_called_once()
            mock_auth_service.generate_tokens.assert_not_called()


class TestRefreshToken:
    """Тесты для POST /auth/refresh"""

    def test_refresh_token_success(self, client):
        """Успешное обновление токенов"""
        refresh_data = RefreshTokenRequest(refresh_token="valid_refresh_token")
        new_tokens = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
        }

        with patch("app.modules.auth.router.auth_service") as mock_auth_service:
            mock_auth_service.refresh_access_token = AsyncMock(return_value=new_tokens)

            response = client.post("/auth/refresh", json=refresh_data.model_dump())

            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["success"] is True
            assert data["code"] == status.HTTP_200_OK
            assert "data" in data
            assert "access_token" in data["data"]
            assert "refresh_token" in data["data"]
            assert data["data"]["access_token"] == "new_access_token"
            assert data["data"]["refresh_token"] == "new_refresh_token"
            mock_auth_service.refresh_access_token.assert_called_once()

    def test_refresh_token_invalid_token(self, client):
        """Обновление токенов с невалидным refresh токеном"""
        refresh_data = RefreshTokenRequest(refresh_token="invalid_token")

        with patch("app.modules.auth.router.auth_service") as mock_auth_service:
            mock_auth_service.refresh_access_token = AsyncMock(
                side_effect=CredentialsException(detail="Invalid refresh token")
            )

            response = client.post("/auth/refresh", json=refresh_data.model_dump())

            assert response.status_code == status.HTTP_401_UNAUTHORIZED
            mock_auth_service.refresh_access_token.assert_called_once()
