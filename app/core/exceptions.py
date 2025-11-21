from typing import Optional
from fastapi import HTTPException, status


class AppException(HTTPException):
    """Базовое исключение приложения"""

    def __init__(
        self, status_code: int, detail: str = "An error occurred", error_code: Optional[str] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code


class NotFoundException(AppException):
    """Ресурс не найден"""

    def __init__(self, detail: str = "Resource not found", error_code: str = "NOT_FOUND"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND, detail=detail, error_code=error_code
        )


class UnauthorizedException(AppException):
    """Не авторизован"""

    def __init__(self, detail: str = "Not authenticated", error_code: str = "UNAUTHORIZED"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, error_code=error_code
        )


class ForbiddenException(AppException):
    """Доступ запрещен"""

    def __init__(self, detail: str = "Forbidden", error_code: str = "FORBIDDEN"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, detail=detail, error_code=error_code
        )


class ValidationException(AppException):
    """Ошибка валидации"""

    def __init__(self, detail: str = "Validation error", error_code: str = "VALIDATION_ERROR"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail, error_code=error_code
        )
