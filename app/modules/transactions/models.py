from sqlalchemy import Column, String, Float, Text, Enum
import enum
from app.shared.base_model import BaseModel


class TransactionType(enum.Enum):
    """Тип транзакции"""
    EXPENSE = "expense"  # Расход
    INCOME = "income"    # Доход


class Transaction(BaseModel):
    """ORM-модель транзакции"""
    __tablename__ = "transactions"

    title = Column(String(200), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    type = Column(Enum(TransactionType), nullable=False, default=TransactionType.EXPENSE)
    
    # Связи (если будут пользователи и группы)
    # user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    # group_id = Column(Integer, ForeignKey("groups.id"), nullable=True)
    
    # relationships
    # user = relationship("User", back_populates="transactions")
    # group = relationship("Group", back_populates="transactions")

