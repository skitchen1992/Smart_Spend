# group_members/router.py
from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.core.dto.response import StandardResponse, success_response
from .schemas import GroupMemberCreate, GroupMemberDelete, GroupMemberResponse
from .service import group_member_service
from app.modules.users.models import User

router = APIRouter(prefix="/group-members", tags=["group_members"])


@router.post("/add_member", response_model=StandardResponse[GroupMemberResponse])
async def add_member(
    data: GroupMemberCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StandardResponse[GroupMemberResponse]:
    """
    Добавить участника в группу.
    Только владелец группы может добавлять участников.
    """
    result = await group_member_service.add(
        db=db, group_id=data.group_id, user_id=data.user_id, requester_id=int(current_user.id)
    )
    return success_response(data=result)


@router.delete("/delete", response_model=StandardResponse[GroupMemberResponse])
async def remove_member(
    data: GroupMemberDelete = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StandardResponse[GroupMemberResponse]:
    """
    Удалить участника из группы.
    Только владелец группы может удалять участников.
    """
    result = await group_member_service.remove(
        db=db, group_id=data.group_id, user_id=data.user_id, requester_id=int(current_user.id)
    )
    return success_response(data=result)
