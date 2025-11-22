# ORM-модель пользователя
from sqlalchemy import Column, String, Boolean
from sqlalchemy.orm import relationship

from app.shared.base_model import BaseModel


class User(BaseModel):
    """ORM-модель пользователя"""

    __tablename__ = "users"

    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(200), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    group_links = relationship(
        "GroupMember",
        back_populates="user")

    groups = relationship(
        "Group",
        secondary="group_members",
        back_populates="members")
    # relationships (если будут связи с группами)
    # groups = relationship("Group", back_populates="users")
