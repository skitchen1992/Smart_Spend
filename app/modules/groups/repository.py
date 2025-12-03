from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.modules.groups.models import Group
from app.modules.groups.models import GroupMember
from app.modules.groups.schemas import GroupCreate
from app.shared.mixins import CRUDMixin
from typing import Optional


class GroupRepository(CRUDMixin[Group]):
    def __init__(self) -> None:
        super().__init__(Group)

    async def get_group(self, db: AsyncSession, group_id: int, id_user: int) -> Optional[Group]:
        """
        Получить группу по ID, но только если указанный пользователь является членом этой группы.

        Args:
            db (AsyncSession): Асинхронная сессия БД.
            group_id (int): ID группы.
            id_user (int): ID пользователя.

        Returns:
        Group | None: Объект группы с загруженными участниками, либо None,
                        если группа не найдена или пользователь не состоит в ней.
        """
        result = await db.execute(
            select(Group)
            .join(GroupMember, GroupMember.group_id == Group.id)
            .where(GroupMember.group_id == group_id, GroupMember.user_id == id_user)
            .options(selectinload(Group.members))
        )
        return result.scalar_one_or_none()

    async def get_with_members(self, db: AsyncSession, group_id: int) -> Optional[Group]:
        """
        Получить группу по ID вместе со списком её участников.

        Args:
            db (AsyncSession): Асинхронная сессия БД.
            group_id (int): ID группы.

        Returns:
            Group | None: Группа с загруженными членами или None, если не найдена.
        """
        result = await db.execute(
            select(Group).where(Group.id == group_id).options(selectinload(Group.members))
        )
        return result.scalar_one_or_none()

    async def get_users_groups(self, db: AsyncSession, user_id: int) -> list[Group]:
        """
        Получить список всех групп, в которых состоит пользователь.

        Args:
            db (AsyncSession): Асинхронная сессия БД.
            user_id (int): ID пользователя.

        Returns:
            list[Group]: Список групп, загруженных со списками участников.
        """
        stmt = (
            select(Group)
            .join(GroupMember, GroupMember.group_id == Group.id)
            .where(GroupMember.user_id == user_id)
            .options(selectinload(Group.members))
        )

        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create_group(self, db: AsyncSession, data: GroupCreate, owner_id: int) -> Group:
        """
        Создать новую группу.

        Args:
            db (AsyncSession): Асинхронная сессия БД.
            data (GroupCreate): Pydantic-схема с данными для создания группы.

        Returns:
            Group: Созданный объект группы.
        """
        group = Group(name=data.name, owner_id=owner_id)
        db.add(group)
        await db.commit()
        return group

    async def delete_group(self, db: AsyncSession, group_id: int) -> None:
        await db.execute(delete(Group).where(Group.id == group_id))
        await db.commit()


group_repository = GroupRepository()
