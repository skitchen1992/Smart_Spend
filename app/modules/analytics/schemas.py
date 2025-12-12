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
    by_group: Dict[str, float] = Field(
        default_factory=dict,
        description="Расходы по группам",
    )
    class Config:
        from_attributes = True

class GroupAnalyticsResponse(BaseModel):
    """Схема ответа с аналитикой по группе"""

    period: str = Field(..., description="Период в формате YYYY-MM для месяца")
    group_id: int = Field(..., description="ID группы")
    group_name: str = Field(..., description="Название группы")
    total_expense: float = Field(default=0.0, description="Общий расход группы за период")
    by_category: Dict[str, float] = Field(
        default_factory=dict,
        description="Расходы группы по категориям",
    )
    member_expenses: Dict[str, float] = Field(
        default_factory=dict,
        description="Расходы каждого участника группы",
    )

    class Config:
        from_attributes = True
