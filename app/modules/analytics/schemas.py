from typing import Dict
from pydantic import BaseModel, Field


class AnalyticsResponse(BaseModel):
    """Схема ответа с аналитикой по расходам"""

    period: str = Field(..., description="Период в формате YYYY-MM для месяца")
    income: float = Field(default=0.0, description="Общий доход за период")
    expense: float = Field(default=0.0, description="Общий расход за период")
    by_category: Dict[str, float] = Field(
        default_factory=dict,
        description="Расходы по категориям",
    )

    class Config:
        from_attributes = True
