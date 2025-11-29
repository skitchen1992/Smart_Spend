from typing import List

from pydantic import BaseModel

class UserRead(BaseModel):
    id: int
    username: str

    class Config:
        from_attribute = True


class Groups(BaseModel):
    name: str

class GroupCreate(BaseModel):
    name: str

class GroupUpdate(BaseModel):
    pass

class GroupDelete(BaseModel):
    group_id: int

class GroupResponse(BaseModel):
    """
    Информация о группе с её участниками

        id (int): ID группы
        members (list): Список пользователей, состоящих в группе
    """
    id: int
    members: List[UserRead] = []

    class Config:
        from_attributes = True

class GroupShort(BaseModel):
    """
    Краткая информация о группе (для списков групп пользователя)

        id (int): ID группы
        name (str): Название группы
    """
    id: int
    name: str

    class Config:
        from_attributes = True


class UserGroupsResponse(BaseModel):
    """
    Список групп, в которых состоит пользователь

            groups (list)
    """
    groups: List[GroupShort]

