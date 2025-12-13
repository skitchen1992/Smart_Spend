from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.core.dto.response import StandardResponse, success_response
from app.modules.groups.service import group_service
from app.modules.groups.schemas import (
    GroupResponse,
    GroupCreate,
    GroupsResponseCreate,
    GroupUpdate,
)
from app.modules.users.models import User

router = APIRouter(prefix="/group", tags=["groups"])


@router.get("/{group_id}", response_model=StandardResponse[GroupResponse])
async def get_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[GroupResponse]:
    """
    Получить информацию о группе по её идентификатору.

    Пользователь может получить информацию только о группах, в которых он является участником.
    """
    group = await group_service.get_group_service(
        db=db, group_id=group_id, id_user=int(current_user.id)
    )

    return success_response(data=group)


@router.post("/create", response_model=StandardResponse[GroupsResponseCreate])
async def create_group(
    data: GroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StandardResponse[GroupsResponseCreate]:
    """
    Создать новую группу.

    Текущий пользователь автоматически становится владельцем созданной группы.

    **Бизнес-правило:** Один пользователь может состоять только в одной группе.
    Если пользователь уже состоит в группе, будет возвращена ошибка.
    """
    new_group = await group_service.create_group_service(
        db=db, data=data, owner_id=int(current_user.id)
    )

    return success_response(data=new_group)


@router.put("/{group_id}/update", response_model=StandardResponse[GroupResponse])
async def update_group(
    group_id: int,
    data: GroupUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[GroupResponse]:
    """
    Обновить информацию о группе.

    Только владелец группы может обновлять её информацию.
    """
    updated_group = await group_service.update_group_service(
        db=db, group_id=group_id, data=data, user_id=int(current_user.id)
    )

    return success_response(data=updated_group)


@router.delete("/{group_id}", response_model=StandardResponse[dict])
async def delete_group(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse[dict]:
    """
    Удалить группу.

    Только владелец группы может удалить её.
    """
    result = await group_service.delete_group_service(
        db=db, group_id=group_id, id_user=int(current_user.id)
    )
    return success_response(data=result)
