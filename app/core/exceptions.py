from typing import Optional
from fastapi import HTTPException, status


class AppException(HTTPException):
    """Базовое исключение приложения"""

    def __init__(
        self, status_code: int, detail: str = "Произошла ошибка", error_code: Optional[str] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code


class NotFoundException(AppException):
    """Ресурс не найден"""

    def __init__(self, detail: str = "Ресурс не найден", error_code: str = "NOT_FOUND"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail=detail, error_code=error_code
        )


class UnauthorizedException(AppException):
    """Не авторизован"""

    def __init__(self, detail: str = "Не авторизован", error_code: str = "UNAUTHORIZED"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, error_code=error_code
        )


class ForbiddenException(AppException):
    """Доступ запрещен"""

    def __init__(self, detail: str = "Доступ запрещен", error_code: str = "FORBIDDEN"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, detail=detail, error_code=error_code
        )


class ValidationException(AppException):
    """Ошибка валидации"""

    def __init__(self, detail: str = "Ошибка валидации", error_code: str = "VALIDATION_ERROR"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail, error_code=error_code
        )


class UserAlreadyExistsException(AppException):
    """Пользователь уже существует"""

    def __init__(
        self, detail: str = "Пользователь уже существует", error_code: str = "USER_EXISTS"
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail, error_code=error_code
        )


class CredentialsException(AppException):
    """Ошибка учетных данных"""

    def __init__(
        self,
        detail: str = "Не удалось проверить учетные данные",
        error_code: str = "INVALID_CREDENTIALS",
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, error_code=error_code
        )
