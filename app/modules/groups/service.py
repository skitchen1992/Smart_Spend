from typing import List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import user

from .repository import group_repository
from .models import Group
from .schemas import GroupResponse, UserRead, GroupShort, UserGroupsResponse


class GroupService:

    async def get_group_service(self, db: AsyncSession, group_id: int, id_user: int) -> GroupResponse:
        """
        Получить информацию о группе, если пользователь имеет к ней доступ.

        Args:
            db (AsyncSession): Асинхронная сессия БД.
            group_id (int): ID группы.
            id_user (int): ID пользователя, пытающегося получить группу.

        Returns:
            GroupResponse: Pydantic-схема с информацией о группе.

        Raises:
            HTTPException: Если пользователь не состоит в группе.
        """
        group = await group_repository.get_group(db, group_id, id_user)

        if not group:
            raise HTTPException(404, "User have no access to this groups")

        members = [UserRead.model_validate({
            "id": user.id,
            "username": user.username
        }) for user in group.members]

        group_response = GroupResponse(
            id=group.id,
            members=members
        )

        return group_response

    async def get_users_groups_service(self, db: AsyncSession, user_id: int) -> UserGroupsResponse:
        """
        Получить список групп, в которых состоит пользователь.

        Args:
            db (AsyncSession): Асинхронная сессия БД.
            user_id (int): ID пользователя.

        Returns:
            UserGroupsResponse: Pydantic-обёртка со списком групп.

        Raises:
            HTTPException: Если пользователь не состоит ни в одной группе.
        """
        groups = await group_repository.get_users_groups(db, user_id)

        if not groups:
            raise HTTPException(404, "User not in any groups")

        groups_response = [
            GroupShort(
                id=group.id,
                name=group.name
            )
            for group in groups
        ]

        return UserGroupsResponse(groups=groups_response)


    async def create_group_service(self, db: AsyncSession, data) -> GroupResponse:
        """
        Создать новую группу.

        Args:
            db (AsyncSession): Асинхронная сессия БД.
            data (GroupCreate): Pydantic-модель с данными для создания группы.

        Returns:
            GroupResponse: Информация о созданной группе.

        Raises:
            HTTPException: Если после создания группа не была найдена (маловероятно).
        """
        group = await group_repository.create_group(db, data)
        group_with_membres = await group_repository.get_with_members(db=db, group_id=group.id)
        if not group_with_membres:
            raise HTTPException(404, "User not found")

        return GroupResponse.model_validate(group_with_membres)

    async def add_user_to_group_service(self, db: AsyncSession, group_id: int, username: str):
        """
        Добавить пользователя в группу.

        Args:
            db (AsyncSession): Асинхронная сессия БД.
            group_id (int): ID группы.
            username (str): Имя пользователя.

        Returns:
            GroupResponse: Группа с обновлённым списком участников.

        Raises:
            HTTPException: Если группа или пользователь не найдены.
        """
        group = await group_repository.get_with_members(db, group_id)
        if not group:
            raise HTTPException(404, "Group not found")

        add_user = await group_repository.add_user(db=db, group_id=group_id, username=username)
        if not add_user:
            raise HTTPException(404, "User not found")

        return GroupResponse.model_validate(add_user)


    async def remove_user_from_group_service(self, db: AsyncSession, group_id: int, username: str):
        """
        Удалить пользователя из группы.

        Args:
            db (AsyncSession): Асинхронная сессия БД.
            group_id (int): ID группы.
            username (str): Имя пользователя.

        Returns:
            GroupResponse: Группа после удаления пользователя.

        Raises:
            HTTPException: Если группа или пользователь не найдены.
        """
        group = await group_repository.get_with_members(db, group_id)
        if not group:
            raise HTTPException(404, "Group not found")

        remove_user = await group_repository.remove_user(db=db, group_id=group_id, username=username)
        if not remove_user:
            raise HTTPException(404, "User not found")

        return GroupResponse.model_validate(remove_user)


group_service = GroupService()
