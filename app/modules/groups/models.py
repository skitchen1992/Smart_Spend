from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.modules.group_members.models import GroupMember
from app.shared.base_model import BaseModel


class Group(BaseModel):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    owner_id = Column(Integer,nullable=False)

    group_links = relationship(
        "GroupMember",
        back_populates="group",
    )

    members = relationship("User", secondary=GroupMember.__table__, back_populates="groups")
