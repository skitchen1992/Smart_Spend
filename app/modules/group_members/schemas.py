# group_members/schemas.py
from pydantic import BaseModel

class GroupMemberCreate(BaseModel):
    group_id: int
    user_id: int  # ID пользователя, которого добавляем

class GroupMemberDelete(BaseModel):
    group_id: int
    user_id: int  # ID пользователя, которого удаляем

class GroupMemberResponse(BaseModel):
    status: str
    message: str = ""
    group_id: int
    user_id: int

    class Config:
        from_attributes = True