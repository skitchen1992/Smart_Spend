from sqlalchemy import Column, String, Float, Text, Enum, Integer, ForeignKey
import enum
from app.shared.base_model import BaseModel


class TransactionType(enum.Enum):
    """Тип транзакции"""
    EXPENSE = "expense"  # Расход
    INCOME = "income"    # Доход


class Transaction(BaseModel):
    """ORM-модель транзакции"""
    __tablename__ = "transactions"

    title = Column(String(100), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True, index=True)
    type = Column(Enum(TransactionType), nullable=False, default=TransactionType.EXPENSE)
    transaction_to_group = Column(Integer, nullable=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Если позже понадобится связь с группой:
    # group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
