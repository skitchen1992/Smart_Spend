from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.shared.base_model import BaseModel

class GroupMember(BaseModel):
    __tablename__ = "group_members"

    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (UniqueConstraint("group_id", "user_id", name="uq_group_user"),)

    group = relationship("Group", back_populates="group_links")
    user = relationship("User", back_populates="group_links")
