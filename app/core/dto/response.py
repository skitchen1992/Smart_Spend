from datetime import datetime
from typing import Any, Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    """Детали ошибки"""

    message: str
    code: Optional[str] = None


class StandardResponse(BaseModel, Generic[T]):
    """Стандартизированный формат ответа API"""

    success: bool = Field(description="Успешность выполнения запроса")
    code: int = Field(description="HTTP код ответа")
    data: Optional[T] = Field(default=None, description="Данные ответа")
    error: Optional[ErrorDetail] = Field(default=None, description="Информация об ошибке")
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z", description="Временная метка"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "code": 200,
                "data": {"user": {"id": 1, "name": "Nikita"}},
                "error": None,
                "timestamp": "2025-11-21T14:12:00Z",
            }
        }


def success_response(data: Any, code: int = 200) -> StandardResponse:
    """Helper функция для создания успешного ответа"""
    return StandardResponse(success=True, code=code, data=data, error=None)
