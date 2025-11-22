from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from .repository import group_member_repository

class GroupMemberService:

    async def add(self, db: AsyncSession, group_id: int, user_id: int):
        exists = await group_member_repository.exists(db, group_id, user_id)
        if exists:
            raise HTTPException(400, "User already in group")

        return await group_member_repository.create(
            db,
            {"group_id": group_id, "user_id": user_id}
        )

    async def remove(self, db: AsyncSession, group_id: int, user_id: int):
        exists = await group_member_repository.exists(db, group_id, user_id)
        if not exists:
            raise HTTPException(400, "User not in group")

        await group_member_repository.remove(db, group_id, user_id)
        return {"status": "ok"}


group_member_service = GroupMemberService()
