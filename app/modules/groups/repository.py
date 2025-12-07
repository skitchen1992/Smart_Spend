from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload

from app.modules.groups.models import Group
from app.modules.groups.models import GroupMember
from app.modules.groups.schemas import GroupCreate, GroupUpdate
from app.shared.mixins import CRUDMixin
from typing import Optional


class GroupRepository(CRUDMixin[Group]):
    def __init__(self) -> None:
        super().__init__(Group)

    async def get_group_by_id(self, db: AsyncSession, group_id: int):
        """
        Получить группу по ID без проверки доступа.
        """
        query = select(Group).where(Group.id == group_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

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

    async def update_group(
            self,
            db: AsyncSession,
            group_id: int,
            data: GroupUpdate,
            user_id: int
    ) -> Optional[Group]:
        """
        Обновить информацию о группе.

        Args:
            db (AsyncSession): Асинхронная сессия БД.
            group_id (int): ID группы.
            data (GroupUpdate): Данные для обновления.
            user_id (int): ID пользователя (должен быть владельцем группы).

        Returns:
            Group | None: Обновлённый объект группы или None, если группа не найдена
                         или пользователь не является владельцем.
        """
        # Проверяем, существует ли группа и является ли пользователь владельцем
        group = await db.execute(
            select(Group)
            .where(Group.id == group_id, Group.owner_id == user_id)
        )
        group = group.scalar_one_or_none()

        if not group:
            return None

        # Подготавливаем данные для обновления
        update_data = {}
        if data.name is not None:
            update_data["name"] = data.name

        if not update_data:
            return group  # Нет данных для обновления

        # Выполняем обновление
        await db.execute(
            update(Group)
            .where(Group.id == group_id)
            .values(**update_data)
        )
        await db.commit()

        # Получаем обновлённую группу
        updated_group = await self.get_with_members(db, group_id)
        return updated_group


    async def delete_group(self, db: AsyncSession, group_id: int, id_user: int) -> bool:
        """
        Удалить группу по ID, если пользователь является владельцем.

        Args:
            db (AsyncSession): Асинхронная сессия БД.
            group_id (int): ID группы.
            id_user (int): ID пользователя.

        Returns:
            bool: True если группа удалена, False если группа не найдена
                  или пользователь не является владельцем.

        Raises:
            HTTPException: Если группа содержит участников помимо владельца.
        """
        # Сначала проверяем, существует ли группа и является ли пользователь владельцем
        group = await db.execute(
            select(Group)
            .where(Group.id == group_id, Group.owner_id == id_user)
            .options(selectinload(Group.members))
        )
        group = group.scalar_one_or_none()

        if not group:
            return False

        # Удаляем саму группу
        await db.execute(
            delete(Group)
            .where(Group.id == group_id)
        )

        await db.commit()
        return True



group_repository = GroupRepository()
