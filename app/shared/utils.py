"""
Хелперы, форматирование, экспорт
"""

from datetime import datetime
from typing import Any


def format_datetime(dt: datetime) -> str:
    """Форматирование datetime в строку"""
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def safe_get(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Безопасное получение значения из вложенного словаря"""
    result: Any = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
        else:
            return default
        if result is None:
            return default
    return result
