from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.exceptions import NotFoundException
from app.core.dto.response import StandardResponse, success_response
from app.modules.groups.service import group_service
from app.modules.groups.schemas import GroupResponse, GroupCreate, UserGroupsResponse

router = APIRouter(prefix="/groups", tags=["groups"])

@router.get("/{group_id}", response_model=StandardResponse[GroupResponse])
async def get_group(
    group_id: int, id_user: int,  db: AsyncSession = Depends(get_db)
) -> StandardResponse[GroupResponse]:
    group = await group_service.get_group_service(db=db, group_id=group_id, id_user=id_user)

    return success_response(data=group)


@router.get("/user/{user_id}/groups", response_model=StandardResponse[UserGroupsResponse])
async def get_users_groups(
        user_id: int,
        db: AsyncSession = Depends(get_db)
) -> StandardResponse[UserGroupsResponse]:
    data = await group_service.get_users_groups_service(db=db, user_id=user_id)
    return success_response(data=data)


@router.post("/", response_model=StandardResponse[GroupResponse])
async def create_group(
        data: GroupCreate, db: AsyncSession = Depends(get_db)
) -> StandardResponse[GroupResponse]:
    new_group = await group_service.create_group_service(db=db, data=data)
    return success_response(data=new_group)

@router.post("/{group_id}/add/{username}", response_model=StandardResponse[GroupResponse])
async def add_user_to_group(
        group_id: int, username: str, db: AsyncSession = Depends(get_db)
) -> StandardResponse[GroupResponse]:
    added_user_to_group = await group_service.add_user_to_group_service(db=db, group_id=group_id, username=username)
    return success_response(data=added_user_to_group)

@router.delete("/{group_id}/remove/{username}", response_model=StandardResponse[GroupResponse])
async def remove_user_from_group(
        group_id: int, username: str, db: AsyncSession = Depends(get_db)
) -> StandardResponse[GroupResponse]:
    removed_user = await group_service.remove_user_from_group_service(db=db, group_id=group_id, username=username)
    return success_response(data=removed_user)




