"""Тесты для app/core/security.py"""

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    create_refresh_token,
    hash_token,
)


class TestPasswordHashing:
    """Тесты для хэширования и проверки паролей"""

    def test_verify_password_correct(self):
        """Проверка верификации правильного пароля"""
        password = "test_password_123"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Проверка верификации неправильного пароля"""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)
        assert verify_password(wrong_password, hashed) is False


class TestAccessToken:
    """Тесты для access токенов"""

    def test_create_access_token_contains_data(self):
        """Проверка что токен содержит переданные данные"""
        data = {"sub": "testuser", "custom": "value"}
        token = create_access_token(data)
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["custom"] == "value"
        assert payload["type"] == "access"

    def test_decode_access_token_invalid(self):
        """Проверка декодирования невалидного токена"""
        invalid_token = "invalid.token.here"
        payload = decode_access_token(invalid_token)
        assert payload is None


class TestRefreshToken:
    """Тесты для refresh токенов"""

    def test_create_refresh_token_contains_data(self):
        """Проверка что refresh токен содержит переданные данные"""
        data = {"sub": "testuser"}
        token, jti = create_refresh_token(data)
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "testuser"
        assert payload["type"] == "refresh"
        assert payload["jti"] == jti


class TestHashToken:
    """Тесты для хэширования токенов"""

    def test_hash_token_consistent(self):
        """Проверка что одинаковые токены дают одинаковый хэш"""
        token = "test_token_string"
        hashed1 = hash_token(token)
        hashed2 = hash_token(token)
        assert hashed1 == hashed2
