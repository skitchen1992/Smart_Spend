from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.shared.mixins import CRUDMixin
from .models import GroupMember

class GroupMemberRepository(CRUDMixin[GroupMember]):

    def __init__(self):
        super().__init__(GroupMember)

    async def exists(self, db: AsyncSession, group_id: int, user_id: int) -> bool:
        q = await db.execute(
            select(GroupMember)
            .where(GroupMember.group_id == group_id)
            .where(GroupMember.user_id == user_id)
        )
        return q.scalar_one_or_none() is not None

    async def remove(self, db: AsyncSession, group_id: int, user_id: int):
        await db.execute(
            delete(GroupMember)
            .where(GroupMember.group_id == group_id)
            .where(GroupMember.user_id == user_id)
        )
        await db.commit()


group_member_repository = GroupMemberRepository()
