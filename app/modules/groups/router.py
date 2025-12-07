from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.core.dto.response import StandardResponse, success_response
from app.modules.groups.service import group_service
from app.modules.groups.schemas import GroupResponse, GroupCreate, UserGroupsResponse, GroupDelete, \
    GroupsResponseCreate, GroupUpdate
from app.modules.users.models import User

router = APIRouter(prefix="/group", tags=["groups"])


@router.get("/{group_id}", response_model=StandardResponse[GroupResponse])
async def get_group(
    group_id: int, current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> StandardResponse[GroupResponse]:
    group = await group_service.get_group_service(db=db, group_id=group_id, id_user=current_user.id)

    return success_response(data=group)


@router.get("/user/{user_id}/groups", response_model=StandardResponse[UserGroupsResponse])
async def get_users_groups(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> StandardResponse[UserGroupsResponse]:
    data = await group_service.get_users_groups_service(db=db, user_id=current_user.id)
    return success_response(data=data)


@router.post("/create", response_model=StandardResponse[GroupsResponseCreate])
async def create_group(
    data: GroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StandardResponse[GroupsResponseCreate]:
    new_group = await group_service.create_group_service(
        db=db, data=data, owner_id=int(current_user.id)
    )

    return success_response(data=new_group)


@router.put("/{group_id}/update", response_model=StandardResponse[GroupResponse])
async def update_group(
        group_id: int,
        data: GroupUpdate,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
) -> StandardResponse[GroupResponse]:
    """
    Обновить информацию о группе.

    Только владелец группы может обновлять её информацию.
    """
    updated_group = await group_service.update_group_service(
        db=db,
        group_id=group_id,
        data=data,
        user_id=current_user.id
    )

    return success_response(data=updated_group)

@router.delete("/delete", response_model=StandardResponse[dict])
async def delete_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> StandardResponse[dict]:
    """Удалить группу."""
    await group_service.delete_group_service(
        db=db,
        group_id=group_id,
        id_user=current_user.id
    )
    return success_response(data={"message": "Group deleted successfully"})