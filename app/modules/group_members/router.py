from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db
from .schemas import GroupMemberCreate, GroupMemberResponse
from .service import group_member_service

router = APIRouter(prefix="/group-members", tags=["group_members"])

@router.post("/add_member", response_model=GroupMemberResponse)
async def add_member(data: GroupMemberCreate, db: AsyncSession = Depends(get_db)):
    return await group_member_service.add(db, data.group_id, data.user_id)


@router.delete("/delete", response_model=dict)
async def remove_member(data: GroupMemberCreate, db: AsyncSession = Depends(get_db)):
    return await group_member_service.remove(db, data.group_id, data.user_id)
