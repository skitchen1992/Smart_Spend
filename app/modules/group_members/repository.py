from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.shared.mixins import CRUDMixin
from .models import GroupMember


class GroupMemberRepository(CRUDMixin[GroupMember]):
    def __init__(self) -> None:
        super().__init__(GroupMember)

    async def exists(self, db: AsyncSession, group_id: int, user_id: int) -> bool:
        q = await db.execute(
            select(GroupMember)
            .where(GroupMember.group_id == group_id)
            .where(GroupMember.user_id == user_id)
        )
        return q.scalar_one_or_none() is not None

    async def user_in_any_group(self, db: AsyncSession, user_id: int) -> bool:
        """
        Проверить, состоит ли пользователь в какой-либо группе.

        Args:
            db: Асинхронная сессия БД
            user_id: ID пользователя

        Returns:
            bool: True если пользователь состоит в какой-либо группе, False иначе
        """
        q = await db.execute(select(GroupMember).where(GroupMember.user_id == user_id))
        return q.scalar_one_or_none() is not None

    async def remove(self, db: AsyncSession, group_id: int, user_id: int) -> None:
        await db.execute(
            delete(GroupMember)
            .where(GroupMember.group_id == group_id)
            .where(GroupMember.user_id == user_id)
        )
        await db.flush()  # Flush для применения изменений, commit делается в сервисе


group_member_repository = GroupMemberRepository()
