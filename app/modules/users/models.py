# ORM-модель пользователя
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship
from app.shared.base_model import BaseModel
from app.modules.auth.models import RefreshToken


class User(BaseModel):
    """ORM-модель пользователя"""

    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(200), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    refresh_tokens = relationship(
        "RefreshToken", back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )

    # groups = relationship("Group", back_populates="users")
