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
    pass

class GroupResponse(BaseModel):
    id: int
    members: List[UserRead] = []

    class Config:
        from_attributes = True

class GroupShort(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class UserGroupsResponse(BaseModel):
    groups: List[GroupShort]

