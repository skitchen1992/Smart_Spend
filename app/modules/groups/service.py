from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import current_user

from .repository import group_repository
from .schemas import GroupResponse, UserRead, GroupShort, UserGroupsResponse, GroupCreate, GroupsResponseCreate
from ..group_members.service import group_member_service


class GroupService:
    async def get_group_service(
        self, db: AsyncSession, group_id: int, id_user: int
    ) -> GroupResponse:
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

        members = [
            UserRead.model_validate({"id": user.id, "username": user.username})
            for user in group.members
        ]

        group_response = GroupResponse(id=int(group.id), members=members)

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

        groups_response = [GroupShort(id=int(group.id), name=str(group.name)) for group in groups]

        return UserGroupsResponse(groups=groups_response)

    async def create_group_service(
        self, db: AsyncSession, data: GroupCreate, owner_id: int
    ) -> GroupsResponseCreate:
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
        group = await group_repository.create_group(db, data, owner_id)

        try:
            await group_member_service.add_owner(
                db=db,
                group_id=int(group.id),
                user_id=owner_id
            )
        except HTTPException as e:
            if e.status_code == 400 and "already exists" in e.detail:
                pass
            else:
                raise e

        await db.refresh(group)

        group_with_membres = await group_repository.get_with_members(db=db, group_id=int(group.id))
        if not group_with_membres:
            raise HTTPException(404, "User not found")

        members = [
            UserRead(
                id=member.id,
                username=member.username
            )
            for member in group_with_membres.members
        ]

        return GroupsResponseCreate(
            id=group_with_membres.id,
            owner_id=group_with_membres.owner_id,
            members=members
        )

    async def delete_group_service(
            self,
            db: AsyncSession,
            group_id: int,
            id_user: int
    ) -> dict:
        """
        Удалить группу (сервисный слой).

        Args:
            db (AsyncSession): Асинхронная сессия БД.
            group_id (int): ID группы.
            id_user (int): ID пользователя.

        Returns:
            dict: Сообщение об успешном удалении.

        Raises:
            HTTPException: Если группа не найдена, пользователь не владелец
                          или в группе есть другие участники.
        """
        try:
            deleted = await group_repository.delete_group(db, group_id, id_user)

            if not deleted:
                raise HTTPException(
                    status_code=404,
                    detail="Group not found or you don't have permission to delete it"
                )

            return {"message": "Group deleted successfully"}

        except HTTPException as e:
            raise e


group_service = GroupService()
