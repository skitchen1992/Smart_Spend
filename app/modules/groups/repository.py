from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete
from sqlalchemy.orm import selectinload

from app.modules.groups.models import Group
from app.modules.groups.models import GroupMember
from app.modules.groups.schemas import GroupCreate
from app.modules.users.models import User
from app.shared.mixins import CRUDMixin

class GroupRepository(CRUDMixin[Group]):

    def __init__(self):
        super().__init__(Group)


    async def get_group(self, db: AsyncSession, group_id: int, id_user: int):
        result = await db.execute(
            select(Group)
            .join(GroupMember, GroupMember.group_id == Group.id)
            .where(GroupMember.group_id == group_id,
                   GroupMember.user_id == id_user)
            .options(selectinload(Group.members))
        )
        return result.scalar_one_or_none()

    async def get_with_members(self, db: AsyncSession, group_id: int):
        result = await db.execute(
            select(Group).where(Group.id == group_id)
            .options(selectinload(Group.members)) )
        return result.scalar_one_or_none()

    async def get_users_groups(self, db: AsyncSession, user_id: int):
        stmt = (
            select(Group)
            .join(GroupMember, GroupMember.group_id == Group.id)
            .where(GroupMember.user_id == user_id)
            .options(selectinload(Group.members))
        )

        result = await db.execute(stmt)
        return result.scalars().all()


    async def create_group(self, db: AsyncSession, data: GroupCreate):
        group = Group(name=data.name)
        db.add(group)
        await db.commit()
        await db.refresh(group)
        return group

    async def add_user(self, db: AsyncSession, group_id: int, username: str):
        # 1. find user
        user = await db.execute(select(User).where(User.username == username))
        user = user.scalar_one_or_none()
        if not user:
            return None

        # 2. insert into group_members
        link = GroupMember(group_id=group_id, user_id=user.id)

        db.add(link)

        await db.commit()
        await db.refresh(link)

        return await self.get_with_members(db, group_id)

    async def remove_user(self, db: AsyncSession, group_id: int, username: str):
        user = await db.execute(select(User).where(User.username == username))
        user = user.scalar_one_or_none()
        if not user:
            return None

        stmt = delete(GroupMember).where(
            (GroupMember.group_id == group_id) &
            (GroupMember.user_id == user.id)
        )

        await db.execute(stmt)
        await db.commit()
        await db.refresh(user)

        return await self.get_with_members(db, group_id)


group_repository = GroupRepository()
